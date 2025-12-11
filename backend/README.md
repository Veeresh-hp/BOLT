# Backend Setup

## Environment
This project uses a virtual environment for dependency management.
An `requirements.txt` file is provided with necessary dependencies.

## Prerequisites
- Python 3.10 (Required for dlib/tensorflow compatibility)
- Visual C++ Redistributable (recommended for OpenCV/dlib)

## Setup
1. Open terminal in `backend` folder.
2. Run `run.bat` (created below) or:
   ```bash
   .\venv\Scripts\activate
   python app.py
   ```

## Troubleshooting
- If `dlib` fails, ensure you have Python 3.10.
- If `mediapipe` fails, ensure you have a compatible Python version (3.8-3.11).
