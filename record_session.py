import os
import csv
import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 16000
DURATION = 6  # seconds given per sentence — generous for any script sentence

SENTENCES = [
    ("hi", "s01", "Aaj mausam bahut accha hai.", ""),
    ("hi", "s02", "Mujhe kitaabein padhna pasand hai.", ""),
    ("hi", "s03", "Kya aap meri madad kar sakte hain?", ""),
    ("hi", "s04", "Hum kal bazaar jaayenge.", ""),
    ("hi", "s05", "Yeh mera pasandeeda gaana hai.", ""),
    ("en", "s01", "The weather is really nice today.", ""),
    ("en", "s02", "I enjoy reading books in my free time.", ""),
    ("en", "s03", "Could you please help me with this?", ""),
    ("en", "s04", "We are planning to visit the market tomorrow.", ""),
    ("en", "s05", "This is one of my favorite songs.", ""),
    ("cs", "s01", "Mujhe office jaana hai, but traffic is really bad today.", "5"),
    ("cs", "s02", "I was going to the market, lekin raaste mein baarish shuru ho gayi.", "7"),
    ("cs", "s03", "Mujhe ye movie bahut pasand aayi, it was really good.", "7"),
    ("cs", "s04", "Can you please send me the file, mujhe abhi chahiye.", "8"),
    ("cs", "s05", "Kal meeting hai office mein, so I need to leave early.", "6"),
    ("cs", "s06", "Pehle hum ghar gaye, then we had dinner, phir movie dekhne gaye.", "5,9"),
]


def record_one_take():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
    sd.wait()
    return audio


def record_session():
    speaker_id = input("Enter speaker ID (e.g. spk01): ").strip()
    os.makedirs("recordings", exist_ok=True)

    metadata_path = "metadata.csv"
    file_exists = os.path.exists(metadata_path)
    metadata_file = open(metadata_path, "a", newline="", encoding="utf-8")
    writer = csv.writer(metadata_file)
    if not file_exists:
        writer.writerow(["filename", "speaker_id", "condition", "sentence_id",
                          "sentence_text", "switch_point_word_index", "notes"])

    for condition, sentence_id, text, switch_point in SENTENCES:
        filename = f"{speaker_id}_{condition}_{sentence_id}.wav"
        filepath = os.path.join("recordings", filename)

        while True:
            print(f"\n>>> Sentence ({condition}): \"{text}\"")
            input("Press ENTER, then start speaking immediately...")
            print(f"Recording for {DURATION} seconds...")
            audio = record_one_take()
            print("Done. Playing it back...")
            sd.play(audio, SAMPLE_RATE)
            sd.wait()

            keep = input("Keep this take? (y = keep, n = redo): ").strip().lower()
            if keep == "y":
                sf.write(filepath, audio, SAMPLE_RATE)
                writer.writerow([filename, speaker_id, condition, sentence_id,
                                  text, switch_point, ""])
                metadata_file.flush()
                print(f"Saved: {filepath}")
                break
            else:
                print("Discarding, let's try again.")

    metadata_file.close()
    print("\nAll 16 sentences recorded and logged in metadata.csv!")


if __name__ == "__main__":
    record_session()
