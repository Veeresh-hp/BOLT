# BOLT

End-to-end demo featuring Lip Reading and Hand Gesture detection with a Flask backend and a React (Create React App) frontend.

## Features
- Lip Reading: Model-driven word prediction from mouth/lip video
- Hand Gestures: MediaPipe + rules/model for gesture recognition
- Live MJPEG preview streamed from backend
- Start/Stop controls with safe camera handoff between modules
- Transcription and gesture text with Save/History/Download in the UI

## Repository Structure
- backend/
  - app.py (Flask server, process management, MJPEG routes)
  - hand_gestures/
    - main.py (gesture detection)
    - frame.jpg (live preview frames)
    - output.txt (latest gesture text)
  - lip reading/
    - src/predict.py (lip reading loop)
    - frame.jpg (live preview frames)
    - output.txt (latest lip text)
  - logs/ (runtime logs)
- frontend/
  - my-app/ (React app)

## Requirements
- Windows 10/11
- Python 3.10+ (project uses a venv at `backend/LH`)
- Node 18+ / npm

Python packages are installed in the existing venv; common deps include: opencv-python, mediapipe, scikit-learn, pandas, TensorFlow, dlib, Pillow.

## Quick Start

1) Backend
- Open a terminal in `backend`
- Activate or use venv directly:
  - Run: `LH\Scripts\python.exe app.py`
- Flask will start at http://127.0.0.1:5000
- Live logs: `backend/logs/lip_reading.log` and `backend/logs/hand_gestures.log`

2) Frontend
- Open a terminal in `frontend/my-app`
- Install deps once: `npm install`
- Start dev server: `npm start`
- App at http://localhost:3000

## How it Works
- Frontend calls backend routes to start/stop subprocesses for either mode.
- Each subprocess writes frames to `frame.jpg` and results to `output.txt`.
- Flask streams frames via:
  - `/video_feed` (hand gestures)
  - `/video_feed_lip` (lip reading)
- Latest text is polled from `/latest_result`.
- Backend ensures only one module uses the camera at a time.

## Useful Endpoints
- `GET /start_hand_gestures` — start gestures
- `GET /stop_hand_gestures` — stop gestures
- `GET /start_lip_reading` — start lip reading
- `GET /stop_lip_reading` — stop lip reading
- `GET /video_feed` — hand gestures MJPEG stream
- `GET /video_feed_lip` — lip reading MJPEG stream
- `GET /latest_result` — current recognized text

## Notes
- If switching modes, the backend pre-stops the other module to free the camera.
- Placeholder "Starting..." frames are written immediately after a module starts to avoid a blank preview.
- On Windows, atomic writes are used (`.tmp` then replace) to avoid file locks.

## Troubleshooting
- If the preview is stuck, stop both modules then start one again.
- Check logs in `backend/logs/` for errors.
- Ensure your webcam is not held by other apps.

## License
MIT
