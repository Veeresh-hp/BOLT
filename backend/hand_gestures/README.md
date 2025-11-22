# Hand-gesture LED controller (OpenCV + MediaPipe + Arduino)

This project counts raised fingers using your webcam and controls five LEDs on an Arduino via Firmata.

## Prerequisites

- Arduino (Uno/Nano/etc.) connected to your PC
- Arduino IDE with StandardFirmata uploaded to the board:
  - Open Arduino IDE → File → Examples → Firmata → StandardFirmata
  - Select your board/port → Upload
- Python 3.9+ on Windows
- Webcam

## Wiring

Connect 5 LEDs (with 220Ω resistors recommended) to Arduino digital pins:
- D13, D12, D11, D10, D9 → LED anodes
- GND → LED cathodes (through resistors)

## Install dependencies

Create/activate a virtual environment (optional) and install:

```powershell
# From the project folder
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Configure COM port

Default is `COM4`. If your board uses a different port, set an environment variable before running:

```powershell
$env:ARDUINO_COMPORT = "COM7"
```

You can also permanently change the default in `controller.py`.

## Run

```powershell
python .\main.py
```

- Show your hand to the camera; the number of raised fingers (0..5) lights the same number of LEDs.
- Press `q` to quit.

## Troubleshooting

- If you see "Could not open Arduino" or no LEDs change:
  - Verify the COM port in Device Manager
  - Ensure StandardFirmata is uploaded
  - Close other apps using the serial port (Arduino Serial Monitor, other programs)
- If `mediapipe` install fails on older Python: use Python 3.9–3.11
- Camera not opening: ensure no other app uses the webcam; change the index in `cv2.VideoCapture(0)` to 1, 2, ...

## Notes

- `controller.cleanup()` is called automatically on exit; it also runs via `atexit` to turn LEDs off and close the board safely.
- You can adjust pin numbers in `controller.py` (`LED_PINS`).
