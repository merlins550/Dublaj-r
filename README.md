# Dublaj-r

This repository contains a simple offline dubbing tool written in Python. The application allows you to select a video or audio file, transcribe it with Whisper, translate the transcript using Argos Translate and then generate a dubbing audio with Balabolka.

## Requirements
- Python 3.10+
- `ffmpeg` installed and available in your `PATH`
- `pywhispercpp` for speech-to-text
- `argos-translate` with the appropriate language packages installed
- `balabolka` (Windows) for text-to-speech

You can install the required Python packages via:

```bash
pip install pywhispercpp argostranslate
```

## Running
Execute the application with:

```bash
python dublaj.py
```

A small GUI will appear allowing you to choose the media file and target language. After processing, an `output.mp3` file will be created in the current directory.
