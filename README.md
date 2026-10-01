# Multilingual & Code-Switched Speech Corpus and Acoustic Analysis

## Overview

This project builds a small labeled speech corpus containing:

- Hindi speech
- English speech
- Hindi-English code-switched speech

Each recording is stored as a WAV file and linked to metadata describing the speaker, language condition, sentence, and code-switch location.

The corpus is then processed using a Python acoustic-analysis pipeline to extract speech features and generate visual quality-control plots.

## Objective

The goal is to create a structured speech dataset and analyze whether measurable acoustic characteristics differ between Hindi, English, and code-switched speech.

The extracted features include:

- Duration
- Pitch / fundamental frequency (F0)
- Energy
- Speaking rate
- MFCCs

The project also generates waveform, spectrogram, and pitch visualizations.

## Recording Conditions

The recording script contains three conditions:

### Hindi

Five Hindi sentences.

### English

Five English sentences.

### Code-switched

Six Hindi-English code-switched sentences.

The code-switched sentences contain manually defined switch-point word indices so that later projects can analyze ASR performance around language-switch boundaries.

## Dataset

The recording pipeline automatically creates:

```text
speaker_condition_sentence.wav

Example:
hamza_hi_s01.wav
hamza_en_s01.wav
hamza_cs_s01.wav

The metadata is stored in:
metadata.csv

The current corpus contains 48 processed recordings.
Pipeline
flowchart TD
    A["Recording prompts"] --> B["Microphone recording"]
    B --> C["16 kHz WAV files"]
    C --> D["metadata.csv"]
    C --> E["Librosa feature extraction"]
    D --> E
    E --> F["Pitch / F0"]
    E --> G["Energy"]
    E --> H["Speaking rate"]
    E --> I["MFCCs"]
    E --> J["Duration"]
    E --> K["QC plots"]
    F --> L["features.csv"]
    G --> L
    H --> L
    I --> L
    J --> L


Tools
- Python
- NumPy
- Pandas
- Librosa
- Matplotlib
- SoundDevice
- SoundFile
Project Structure
project1-speech-corpus/
│
├── recordings/
│   └── *.wav
│
├── plots/
│   ├── qc_*.png
│   └── compare_*.png
│
├── record_session.py
├── extract_features.py
├── metadata.csv
├── features.csv
├── requirements.txt
├── .gitignore
└── README.md

Recording Pipeline
record_session.py:
1. Displays a sentence.
2. Records a fixed-duration audio take.
3. Plays the recording back.
4. Allows the speaker to keep or redo the take.
5. Saves the WAV file.
6. Automatically records the corresponding metadata.
Feature Extraction
extract_features.py processes each recording and extracts acoustic measurements.
The analysis uses a 16 kHz sampling rate and speech-oriented short-time analysis parameters.
The pipeline also includes quality checks for silent recordings and pitch estimates occurring near the configured pitch floor.
Outputs
metadata.csv
Contains:
- filename
- speaker ID
- condition
- sentence ID
- sentence text
- switch-point word index
- notes
features.csv
Contains one row per successfully processed recording and the extracted acoustic measurements.
plots/
Contains:
- Per-recording waveform plots
- Spectrograms
- Pitch tracks
- Feature comparison plots across language conditions
Reproducibility
Create a virtual environment:
python -m venv venv

Activate it on Windows:
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Run the feature extraction pipeline:
python extract_features.py

Result
The corpus and acoustic-analysis pipeline were executed on real speech recordings.
The resulting features.csv contains the measurements produced by the actual recordings, while the plots/ directory provides visual quality checks and condition-level comparisons.
Connection to Later Projects
Project 1 provides the labeled speech corpus used by Project 2 for ASR evaluation.
The switch_point_word_index metadata is later used by Project 2 to investigate whether transcription errors occur near annotated language-switch boundaries.
Project 3 and Project 4 build additional real-time speech-processing components on top of this work.

Save with:

```text
Ctrl + S

The README reflects the actual scope of Project 1 in your supplied document: labeled Hindi/English/code-switched recordings, feature extraction, plots, and comparison analysis.