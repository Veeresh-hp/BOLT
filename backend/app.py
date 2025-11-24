from flask import Flask, jsonify, Response
import subprocess
import threading
from flask_cors import CORS
import os
import cv2
import time
import sys

app = Flask(__name__)
CORS(app)

# To store last recognized output
latest_result = {"type": None, "text": ""}
_threads = {}

# --------------------- #
# Helper Functions
# --------------------- #
def read_output_file(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print("Error reading output file:", e)
    return ""

def ensure_removed(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# --------------------- #
# LIP READING
# --------------------- #
def run_lip_reading():
    global latest_result
    base_dir = os.path.dirname(__file__)
    venv_python = os.path.join(base_dir, "LH", "Scripts", "python.exe")
    predict_script = os.path.join(base_dir, "lip reading", "src", "predict.py")
    output_file = os.path.join(base_dir, "lip reading", "output.txt")
    stop_file = os.path.join(base_dir, "lip reading", "stop.txt")
    frame_file = os.path.join(base_dir, "lip reading", "frame.jpg")

    ensure_removed(output_file)
    ensure_removed(stop_file)

    if not os.path.exists(venv_python):
        print("⚠️  venv python not found, will fallback to system python if available:", venv_python)

    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "lip_reading.log")
    try:
        print("▶️ Starting Lip Reading subprocess (Popen)...")
        with open(log_path, "a", encoding="utf-8") as lf:
            # choose the python executable: prefer venv, else use the running interpreter
            python_exec = venv_python if os.path.exists(venv_python) else sys.executable
            print(f"[DEBUG] lip_reading will use python_exec={python_exec}")
            cmd = [python_exec, predict_script]
            proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=os.path.dirname(predict_script))
            # store process so it can be inspected by other endpoints if needed
            _threads['lip_reading_proc'] = proc
            print(f"LipReading Popen started pid={proc.pid}")
            # create a placeholder frame for lip-reading immediately
            try:
                import numpy as _np
                H, W = 480, 640
                placeholder = _np.zeros((H, W, 3), dtype=_np.uint8)
                try:
                    import cv2 as _cv2
                    txt = 'Starting...'
                    font = _cv2.FONT_HERSHEY_SIMPLEX
                    scale = 1.6
                    thickness = 3
                    (tw, th), _ = _cv2.getTextSize(txt, font, scale, thickness)
                    x = max(10, (W - tw) // 2)
                    y = max(th + 10, (H + th) // 2)
                    _cv2.putText(placeholder, txt, (x, y), font, scale, (255, 255, 255), thickness, _cv2.LINE_AA)
                except Exception:
                    pass
                try:
                    from PIL import Image as _Image
                    im = _Image.fromarray(placeholder[:, :, ::-1])
                    tmp = frame_file + ".tmp"
                    im.save(tmp, format='JPEG', quality=85)
                    try:
                        os.replace(tmp, frame_file)
                    except Exception:
                        os.rename(tmp, frame_file)
                except Exception:
                    try:
                        import cv2 as _cv2
                        _cv2.imwrite(frame_file, placeholder)
                    except Exception as e:
                        print('[WARN] Could not write lip placeholder frame:', e)
            except Exception as e:
                print('[WARN] Could not write lip placeholder frame:', e)
    except Exception as e:
        print("❌ Lip Reading error:", e)

    text = read_output_file(output_file)
    latest_result = {"type": "lip-reading", "text": text or "No output"}


# --------------------- #
# HAND GESTURES
# --------------------- #
def run_hand_gestures():
    global latest_result
    base_dir = os.path.dirname(__file__)
    venv_python = os.path.join(base_dir, "LH", "Scripts", "python.exe")
    main_script = os.path.join(base_dir, "hand_gestures", "main.py")
    output_file = os.path.join(base_dir, "hand_gestures", "output.txt")
    stop_file = os.path.join(base_dir, "hand_gestures", "stop.txt")
    frame_file = os.path.join(base_dir, "hand_gestures", "frame.jpg")

    ensure_removed(output_file)
    ensure_removed(stop_file)

    if not os.path.exists(venv_python):
        print("⚠️  venv python not found, will fallback to system python if available:", venv_python)

    logs_dir = os.path.join(base_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, "hand_gestures.log")
    try:
        print("▶️ Starting Hand Gesture subprocess (Popen)...")
        with open(log_path, "a", encoding="utf-8") as lf:
            python_exec = venv_python if os.path.exists(venv_python) else sys.executable
            print(f"[DEBUG] hand_gestures will use python_exec={python_exec}")
            cmd = [python_exec, main_script]
            proc = subprocess.Popen(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=os.path.dirname(main_script))
            _threads['hand_gestures_proc'] = proc
            print(f"HandGesture Popen started pid={proc.pid}")
            # create a small placeholder frame so frontend has something to display immediately
            try:
                import numpy as _np
                placeholder = _np.zeros((240, 320, 3), dtype=_np.uint8)
                try:
                    import cv2 as _cv2
                    _cv2.putText(placeholder, 'Starting...', (10, 120), _cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                except Exception:
                    pass
                # Try Pillow first for reliable JPEG writing
                try:
                    from PIL import Image as _Image
                    im = _Image.fromarray(placeholder[:, :, ::-1])
                    tmp = frame_file + ".tmp"
                    im.save(tmp, format='JPEG', quality=85)
                    try:
                        os.replace(tmp, frame_file)
                    except Exception:
                        os.rename(tmp, frame_file)
                except Exception:
                    try:
                        import cv2 as _cv2
                        _cv2.imwrite(frame_file, placeholder)
                    except Exception as e:
                        print('[WARN] Could not write placeholder frame:', e)
            except Exception as e:
                print('[WARN] Could not write placeholder frame:', e)
    except Exception as e:
        print("❌ Hand gesture error:", e)

    text = read_output_file(output_file)
    latest_result = {"type": "hand-gesture", "text": text or "No output"}


# --------------------- #
# FLASK ROUTES
# --------------------- #
@app.route("/")
def home():
    return jsonify({"message": "Backend running successfully 🚀"})


@app.route("/start_lip_reading", methods=["GET"])
def start_lip_reading():
    # If a previous subprocess exists, try to stop it first (prevents camera lock)
    try:
        proc = _threads.get('lip_reading_proc')
        if proc is not None:
            print(f"[INFO] Pre-stop existing lip_reading proc pid={getattr(proc, 'pid', None)}")
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    except Exception as e:
        print('[WARN] Failed to pre-stop existing lip_reading subprocess:', e)

    t = threading.Thread(target=run_lip_reading, daemon=True)
    t.start()
    _threads["lip_reading"] = t
    return jsonify({"status": "Lip Reading started"})


@app.route("/stop_lip_reading", methods=["GET"])
def stop_lip_reading():
    base_dir = os.path.dirname(__file__)
    stop_file = os.path.join(base_dir, "lip reading", "stop.txt")
    try:
        os.makedirs(os.path.dirname(stop_file), exist_ok=True)
        with open(stop_file, "w") as f:
            f.write("stop")
        # also try to terminate the subprocess if it was started (free the camera quickly)
        try:
            proc = _threads.get('lip_reading_proc')
            if proc is not None:
                print(f"[INFO] Attempting to terminate lip_reading proc pid={getattr(proc, 'pid', None)}")
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        except Exception as e:
            print('[WARN] Failed to terminate lip_reading subprocess:', e)
        return jsonify({"status": "stop signal written for lip reading"})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500


@app.route("/start_hand_gestures", methods=["GET"])
def start_hand_gestures():
    # Stop lip-reading subprocess if running to avoid camera contention
    try:
        proc = _threads.get('lip_reading_proc')
        if proc is not None:
            print(f"[INFO] Pre-stop existing lip_reading proc pid={getattr(proc, 'pid', None)}")
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    except Exception as e:
        print('[WARN] Failed to pre-stop existing lip_reading subprocess:', e)

    t = threading.Thread(target=run_hand_gestures, daemon=True)
    t.start()
    _threads["hand_gestures"] = t
    return jsonify({"status": "Hand Gesture recognition started"})


@app.route("/stop_hand_gestures", methods=["GET"])
def stop_hand_gestures():
    base_dir = os.path.dirname(__file__)
    stop_file = os.path.join(base_dir, "hand_gestures", "stop.txt")
    try:
        os.makedirs(os.path.dirname(stop_file), exist_ok=True)
        with open(stop_file, "w") as f:
            f.write("stop")
        # also try to terminate the subprocess if it was started
        try:
            proc = _threads.get('hand_gestures_proc')
            if proc is not None:
                print(f"[INFO] Attempting to terminate hand_gestures proc pid={getattr(proc, 'pid', None)}")
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        except Exception as e:
            print('[WARN] Failed to terminate hand_gestures subprocess:', e)
        return jsonify({"status": "stop signal written for hand gestures"})
    except Exception as e:
        return jsonify({"status": "failed", "error": str(e)}), 500


@app.route("/latest_result", methods=["GET"])
def get_latest_result():
    # Return output for the subprocess that is currently running to match the active tab
    base_dir = os.path.dirname(__file__)
    hg_out = os.path.join(base_dir, "hand_gestures", "output.txt")
    lr_out = os.path.join(base_dir, "lip reading", "output.txt")

    def _alive(key):
        try:
            p = _threads.get(key)
            return (p is not None) and (getattr(p, 'poll', lambda: None)() is None)
        except Exception:
            return False

    # 1) If hand gestures are running, return their output first
    if _alive('hand_gestures_proc'):
        try:
            if os.path.exists(hg_out):
                text = read_output_file(hg_out)
                if text:
                    return jsonify({"type": "hand-gesture", "text": text})
        except Exception as e:
            print('[WARN] Error reading hand gesture output:', e)

    # 2) If lip reading is running, return its output next
    if _alive('lip_reading_proc'):
        try:
            if os.path.exists(lr_out):
                text = read_output_file(lr_out)
                if text:
                    return jsonify({"type": "lip-reading", "text": text})
        except Exception as e:
            print('[WARN] Error reading lip reading output:', e)

    # 3) Fallback: prefer the most recently updated file
    try:
        lr_m = os.path.getmtime(lr_out) if os.path.exists(lr_out) else -1
        hg_m = os.path.getmtime(hg_out) if os.path.exists(hg_out) else -1
        if lr_m >= hg_m and lr_m != -1:
            text = read_output_file(lr_out)
            if text:
                return jsonify({"type": "lip-reading", "text": text})
        if hg_m > lr_m and hg_m != -1:
            text = read_output_file(hg_out)
            if text:
                return jsonify({"type": "hand-gesture", "text": text})
    except Exception:
        pass

    # 4) Final fallback
    return jsonify(latest_result)


# --------------------- #
# VIDEO STREAM ROUTES
# --------------------- #
camera = None

def generate_frames():
    global camera
    base_dir = os.path.dirname(__file__)
    frame_file = os.path.join(base_dir, "hand_gestures", "frame.jpg")

    # If a processed frame file exists (written by hand_gestures/main.py), stream it.
    # Otherwise fall back to direct camera capture.
    while True:
        try:
            if os.path.exists(frame_file):
                try:
                    with open(frame_file, 'rb') as f:
                        data = f.read()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
                except Exception as e:
                    # if read fails, fall back to camera for this iteration
                    print("[WARN] Failed to read frame file:", e)
                    time.sleep(0.05)
                    continue
            else:
                # fallback to reading directly from camera
                if camera is None:
                    camera = cv2.VideoCapture(0)
                success, frame = camera.read()
                if not success or frame is None:
                    time.sleep(0.05)
                    continue
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except GeneratorExit:
            # client disconnected
            break
        except Exception as e:
            print("[ERROR] generate_frames error:", e)
            time.sleep(0.1)

@app.route("/video_feed")
def video_feed():
    """Stream webcam feed to frontend for hand gestures"""
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/video_feed_lip")
def video_feed_lip():
    """Stream the MJPEG frames produced by the lip-reading subprocess."""
    base_dir = os.path.dirname(__file__)
    frame_file = os.path.join(base_dir, "lip reading", "frame.jpg")

    def gen():
        last_frame = None
        retry_count = 0
        max_retries = 3
        
        while True:
            try:
                if os.path.exists(frame_file):
                    data = None
                    # Try multiple times to read the file (handle Windows file locks)
                    for attempt in range(5):
                        try:
                            with open(frame_file, 'rb') as f:
                                data = f.read()
                            if data and len(data) > 0:
                                last_frame = data
                                retry_count = 0
                                break
                        except PermissionError:
                            if attempt < 4:
                                time.sleep(0.02)
                                continue
                        except Exception as e:
                            if attempt < 4:
                                time.sleep(0.02)
                                continue
                            else:
                                print(f"[WARN] Failed to read lip frame after {attempt+1} attempts:", e)
                                break
                    
                    # If we got data, send it
                    if data and len(data) > 0:
                        yield (
                            b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n'
                        )
                        time.sleep(0.033)  # ~30 FPS
                    # If we failed but have a last frame, send that
                    elif last_frame is not None:
                        yield (
                            b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n'
                        )
                        time.sleep(0.1)
                    else:
                        time.sleep(0.1)
                else:
                    # Frame file doesn't exist yet - wait for it
                    retry_count += 1
                    if retry_count > max_retries:
                        # Send a placeholder if we've waited too long
                        if last_frame is not None:
                            yield (
                                b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\r\n' + last_frame + b'\r\n'
                            )
                    time.sleep(0.2)
                    
            except GeneratorExit:
                print("[INFO] Client disconnected from lip video feed")
                break
            except Exception as e:
                print("[ERROR] video_feed_lip error:", e)
                time.sleep(0.2)

    # Important: do not force 'Connection: close' here; browsers keep MJPEG streams open
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


# --------------------- #
# START FLASK APP
# --------------------- #
if __name__ == "__main__":
    print("Starting backend on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)