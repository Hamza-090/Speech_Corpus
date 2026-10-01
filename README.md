# Project 1 — Multilingual & Code-Switched Speech Corpus and Acoustic Analysis

## Overview
This project builds a small, structured, labeled speech corpus containing Hindi speech, English speech, and Hindi-English code-switched speech. Each recording is stored as a `.wav` file and linked to a comprehensive metadata log detailing the speaker, language condition, sentence, and exact code-switch location. 

The corpus is processed using a custom Python acoustic-analysis pipeline to extract core speech features and generate visual quality-control (QC) plots, establishing a foundation for analyzing acoustic characteristic differences across language conditions.

## Objective
The primary goal is to construct a highly organized speech dataset and determine whether measurable acoustic features differ significantly between Hindi, English, and code-switched speech. 

Extracted acoustic features include:
*   **Duration**
*   **Pitch / Fundamental Frequency (F0)**
*   **Energy**
*   **Speaking Rate**
*   **Mel-Frequency Cepstral Coefficients (MFCCs)**

## Dataset & Recording Conditions
The current corpus contains **48 processed recordings**. The recording script encompasses three specific conditions:

*   **Hindi:** 5 distinct Hindi sentences.
*   **English:** 5 distinct English sentences.
*   **Code-Switched (CS):** 6 Hindi-English code-switched sentences. The CS sentences contain manually defined switch-point word indices, enabling downstream analysis of Automatic Speech Recognition (ASR) performance specifically around language-switch boundaries.

**File Naming Convention:**  
Recordings are automatically saved and formatted as `speaker_condition_sentence.wav`.  
*Examples:* `hamza_hi_s01.wav`, `hamza_en_s01.wav`, `hamza_cs_s01.wav`

## Project Structure
```text
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
