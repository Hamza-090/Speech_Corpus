Example:
hamza_hi_s01.wav
hamza_en_s01.wav
hamza_cs_s01.wav

The metadata is stored in:
metadata.csv

The current corpus contains 48 processed recordings.
Pipeline
    ```mermaid
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
    ```



Tools
- Python
- NumPy
- Pandas
- Librosa
- Matplotlib
- SoundDevice
- SoundFile
# Project Structure
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
