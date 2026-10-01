import os

import numpy as np
import pandas as pd
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")                     
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Settings. Every number has a reason.
# ---------------------------------------------------------------------------
SAMPLE_RATE = 16000    # samples per second (same as the recording script)
N_FFT = 400            # 400 samples = 25 ms analysis window
HOP = 160              # 160 samples = 10 ms step between windows
N_MELS = 40            # number of mel filters
N_MFCC = 13            # how many MFCCs to keep
PITCH_MIN = 60         # Hz: lowest pitch pYIN may report
PITCH_MAX = 500        # Hz: highest pitch pYIN may report
PITCH_FRAME = 1024     # 64 ms window for pitch (must hold 2+ periods of PITCH_MIN)
SILENCE_DB = 30        # a frame this many dB below the loudest frame counts as silence

AUDIO_DIR = "recordings"
PLOTS_DIR = "plots"
CONDITION_ORDER = ["hi", "en", "cs"]


def extract_features(filepath, sentence_text):
    """Measure one recording. Returns (row, extras)."""
    # 1. Load the file as an array of numbers between -1 and 1, at 16,000 samples/second.
    y_full, sr = librosa.load(filepath, sr=SAMPLE_RATE, mono=True)
    raw_duration = len(y_full) / sr

    # 1b. Reject a file with (near) no signal at all before any ratio/dB math runs on
    # it -- trim() has no "loud" reference to compare against in true silence, so it
    # would otherwise wave the whole clip through as "kept", and every dB-relative
    # calculation downstream would divide by ~0. Caught here once, instead of as NaNs
    # scattered through five different columns of features.csv.
    if np.abs(y_full).max() < 1e-4:
        raise ValueError("file is silent (no signal above the noise floor) -- re-record it")

    # 2. Cut the silence at the start and end. What is left is the "speech span".
    y, (start, end) = librosa.effects.trim(
        y_full, top_db=SILENCE_DB, frame_length=N_FFT, hop_length=HOP
    )
    speech_duration = len(y) / sr
    if speech_duration < 0.3:
        raise ValueError("almost no speech found (silent file, or SILENCE_DB too strict)")

    # 3. Loudness of every 10 ms frame, in dB relative to the loudest frame (0 dB).
    rms = librosa.feature.rms(y=y, frame_length=N_FFT, hop_length=HOP)[0]
    rms_db = 20 * np.log10(rms / rms.max() + 1e-10)
    active = rms_db > -SILENCE_DB          # True where there is speech-level energy

    # 4. Pitch with pYIN, but only trusted in frames that are loud enough.
    f0, voiced_flag, voiced_prob = librosa.pyin(
        y, fmin=PITCH_MIN, fmax=PITCH_MAX, sr=sr,
        frame_length=PITCH_FRAME, hop_length=HOP,
    )
    assert len(f0) == len(rms), "pitch and loudness frames should line up"
    # pYIN occasionally can't find real periodicity in a quiet, noisy frame and
    # collapses to the exact edge of the search range instead of returning NaN --
    # a frame reporting a pitch sitting right on PITCH_MIN is a search artefact,
    # not a real measurement, so it is dropped along with the energy gate.
    at_floor = f0 <= PITCH_MIN * 1.02
    voiced = ~np.isnan(f0) & active & ~at_floor
    median_pitch = float(np.median(f0[voiced])) if voiced.any() else float("nan")
    voiced_fraction = float(voiced.sum() / active.sum())

    # 5. Loudness summary and speaking rate (words per second of speech).
    mean_energy = float(np.mean(rms))
    n_words = len(sentence_text.split())
    speaking_rate = n_words / speech_duration

    # 6. MFCCs: a (13 x frames) grid, averaged over time into 13 numbers.
    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=N_MFCC, n_fft=N_FFT, hop_length=HOP, n_mels=N_MELS
    )
    mfcc_mean = mfcc.mean(axis=1)

    row = {
        "raw_duration_sec": raw_duration,
        "speech_duration_sec": speech_duration,
        "median_pitch_hz": median_pitch,
        "voiced_fraction": voiced_fraction,
        "mean_energy": mean_energy,
        "speaking_rate_wps": speaking_rate,
    }
    for i, value in enumerate(mfcc_mean, start=1):
        row[f"mfcc_{i}"] = float(value)

    extras = {"y_full": y_full, "sr": sr, "start": start, "end": end,
              "f0": f0, "voiced": voiced}
    return row, extras


def plot_qc(extras, title, save_path):
    """Quality-check picture: what was kept, what the spectrum looks like, where pitch was found."""
    y_full, sr = extras["y_full"], extras["sr"]
    start, end = extras["start"], extras["end"]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    librosa.display.waveshow(y_full, sr=sr, ax=axes[0])
    axes[0].axvspan(start / sr, end / sr, color="green", alpha=0.15)
    axes[0].set_title(f"{title}   |   waveform (green = kept as speech)")
    axes[0].set_ylabel("amplitude")

    D = librosa.stft(y_full, n_fft=N_FFT, hop_length=HOP)
    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
    librosa.display.specshow(S_db, sr=sr, hop_length=HOP, x_axis="time", y_axis="hz", ax=axes[1])
    axes[1].set_title("spectrogram (dB, 0 = loudest)")

    t = librosa.times_like(extras["f0"], sr=sr, hop_length=HOP) + start / sr
    pitch_to_plot = np.where(extras["voiced"], extras["f0"], np.nan)
    axes[2].plot(t, pitch_to_plot, ".", markersize=3)
    axes[2].set_ylim(0, PITCH_MAX)
    axes[2].set_ylabel("pitch (Hz)")
    axes[2].set_xlabel("time (s)")
    axes[2].set_title("pitch (only in frames loud enough to trust)")

    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close(fig)


def plot_comparison(df, feature_name, save_path):
    """Box plot per language condition, with every recording drawn as a dot coloured by speaker."""
    data = df.dropna(subset=[feature_name])
    conditions = [c for c in CONDITION_ORDER if c in set(data["condition"])]
    groups = [data.loc[data["condition"] == c, feature_name].values for c in conditions]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.boxplot(groups, showfliers=False)
    ax.set_xticks(range(1, len(conditions) + 1))
    ax.set_xticklabels(conditions)

    rng = np.random.default_rng(0)
    palette = plt.get_cmap("tab10")
    labelled = set()
    for i, speaker in enumerate(sorted(data["speaker_id"].unique())):
        for j, cond in enumerate(conditions, start=1):
            vals = data.loc[(data["condition"] == cond) & (data["speaker_id"] == speaker),
                            feature_name].values
            label = speaker if speaker not in labelled else None
            labelled.add(speaker)
            ax.scatter(j + rng.uniform(-0.15, 0.15, len(vals)), vals,
                       s=24, color=palette(i % 10), alpha=0.85, label=label)

    ax.set_title(f"{feature_name} by language condition")
    ax.set_ylabel(feature_name)
    ax.legend(title="speaker")
    plt.tight_layout()
    plt.savefig(save_path, dpi=100)
    plt.close(fig)


def main():
    os.makedirs(PLOTS_DIR, exist_ok=True)
    metadata = pd.read_csv("metadata.csv")

    rows, problems = [], []
    for i, meta in metadata.iterrows():
        filename = meta["filename"]
        print(f"[{i + 1}/{len(metadata)}] {filename}")
        try:
            row, extras = extract_features(os.path.join(AUDIO_DIR, filename), meta["sentence_text"])
        except Exception as err:               # one bad file must not stop the whole run
            print(f"    SKIPPED: {err}")
            problems.append((filename, str(err)))
            continue
        row["filename"] = filename
        row["speaker_id"] = meta["speaker_id"]
        row["condition"] = meta["condition"]
        rows.append(row)
        plot_qc(extras, filename, os.path.join(PLOTS_DIR, f"qc_{filename}.png"))

    if not rows:
        print("No recordings could be measured. Check metadata.csv and the recordings folder.")
        return

    features = pd.DataFrame(rows)
    first = ["filename", "speaker_id", "condition"]
    features = features[first + [c for c in features.columns if c not in first]]
    features.to_csv("features.csv", index=False)
    print(f"\nSaved {len(features)} rows to features.csv")

    for feature in ["median_pitch_hz", "mean_energy", "speaking_rate_wps"]:
        plot_comparison(features, feature, os.path.join(PLOTS_DIR, f"compare_{feature}.png"))
    print("Saved comparison plots to plots/")

    if problems:
        print(f"\n{len(problems)} file(s) were skipped:")
        for name, why in problems:
            print(f"  {name}: {why}")


if __name__ == "__main__":
    main()