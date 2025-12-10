import cv2
import mediapipe as mp
import time
import csv
import os
import shutil
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import controller as cnt  # optional Arduino controller; ensure safe import if not present

# Config
THIS_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(THIS_DIR, "gesture_data.csv")
MODEL_FILE = os.path.join(THIS_DIR, "gesture_model.pkl")
OUTPUT_FILE = os.path.join(THIS_DIR, "output.txt")
STOP_FILE = os.path.join(THIS_DIR, "stop.txt")
FRAME_FILE = os.path.join(THIS_DIR, "frame.jpg")
TRAINING_MODE = False  # set True if you want to collect labelled data

time.sleep(1.0)

# remove stale stop file if present (prevents the script from instantly exiting when started)
try:
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
        print("[INFO] Removed stale stop file at startup.")
except Exception:
    pass

# MediaPipe setup
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]

def open_camera(device=0, retries=10, delay=0.8):
    """Try to open the camera with retries. Returns a VideoCapture object or None."""
    # Try a couple of backends: prefer CAP_DSHOW on Windows, then fallback to default
    for attempt in range(1, retries + 1):
        for backend in (getattr(cv2, 'CAP_DSHOW', None), None):
            try:
                if backend is None:
                    cap = cv2.VideoCapture(device)
                else:
                    cap = cv2.VideoCapture(device, backend)
                opened = cap.isOpened()
                print(f"[INFO] Camera attempt {attempt}/{retries} backend={backend} opened={opened}")
                if opened:
                    return cap
                try:
                    cap.release()
                except Exception:
                    pass
            except Exception as e:
                print(f"[WARN] Camera open backend={backend} failed: {e}")
        time.sleep(delay)
    print("[ERROR] Unable to open camera after retries")
    return None

video = open_camera(0)

def save_landmarks(label, lmList):
    file_exists = os.path.exists(DATA_FILE)
    with open(DATA_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            header = ["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)]
            writer.writerow(header)
        if len(lmList) != 21:
            print(f"[WARN] Skipped sample for '{label}' - expected 21 landmarks, got {len(lmList)}.")
            return
        row = [label] + [p[1] for p in lmList] + [p[2] for p in lmList]
        writer.writerow(row)
        print(f"[INFO] Saved {label} sample.")

def clean_dataset_file() -> str:
    if not os.path.exists(DATA_FILE):
        return DATA_FILE
    tmp_rows = []
    kept, fixed, skipped = 0, 0, 0
    with open(DATA_FILE, newline="") as fin:
        reader = csv.reader(fin)
        try:
            header = next(reader)
        except StopIteration:
            header = None
        correct_header = ["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)]
        tmp_rows.append(correct_header)
        for row in reader:
            n = len(row)
            if n == 43:
                tmp_rows.append(row)
                kept += 1
            elif n == 85:
                label = row[0]
                xs = row[1:1+42][:21]
                ys = row[1+42:1+42+42][:21]
                fixed_row = [label] + xs + ys
                tmp_rows.append(fixed_row)
                fixed += 1
            else:
                skipped += 1
    try:
        shutil.copy2(DATA_FILE, DATA_FILE + ".bak")
    except Exception:
        pass
    with open(DATA_FILE, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerows(tmp_rows)
    print(f"[INFO] Cleaned dataset: kept={kept}, fixed={fixed}, skipped={skipped}. Backup at {DATA_FILE}.bak")
    return DATA_FILE

def train_model():
    import pandas as pd
    if not os.path.exists(DATA_FILE):
        print("[ERROR] No training data found.")
        return False
    clean_dataset_file()
    df = pd.read_csv(DATA_FILE)
    X = df.drop("label", axis=1)
    y = df["label"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    joblib.dump(model, MODEL_FILE)
    print(f"[INFO] Model trained. Accuracy: {acc:.2f}")
    return True

def classify_gesture(lmList, model):
    row = np.array([p[1] for p in lmList] + [p[2] for p in lmList]).reshape(1, -1)
    return model.predict(row)[0]

model = None
if not TRAINING_MODE and os.path.exists(MODEL_FILE):
    model = joblib.load(MODEL_FILE)
    print("[INFO] Loaded trained model for classification.")

try:
    with mp_hand.Hands(min_detection_confidence=0.5,
                       min_tracking_confidence=0.5) as hands:
        # track last written text to avoid noisy repeated writes
        last_text = ""
        while True:
            # graceful stop if stop file exists
            if os.path.exists(STOP_FILE):
                print("[INFO] Stop file found - exiting hand_gestures loop.")
                break

            # Ensure video capture is available; try reopening if needed
            if video is None or not getattr(video, 'isOpened', lambda: False)():
                print("[WARN] Camera not opened, attempting to reopen...")
                video = open_camera(0)
                if video is None:
                    time.sleep(0.5)
                    continue

            ret, image = video.read()
            if not ret or image is None:
                print("[WARN] Could not read frame from camera (ret=False). Retrying...")
                time.sleep(0.2)
                continue

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            lmList = []
            if results.multi_hand_landmarks:
                # Draw landmarks for all detected hands
                for hand_landmark in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)
                first_hand = results.multi_hand_landmarks[0]
                h, w, c = image.shape
                for id, lm in enumerate(first_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

            if len(lmList) != 0:
                if TRAINING_MODE:
                    # headless mode: keyboard-based landmark saving not available
                    # If you need to collect labeled data, use a separate collection script
                    pass
                else:
                    if model is not None:
                        gesture = classify_gesture(lmList, model)
                        # prepare new text and write only when it changes
                        try:
                            new_text = f"Recognized Gesture: {gesture}"
                            if new_text != last_text:
                                try:
                                    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                                        f.write(new_text)
                                        f.flush()
                                        try:
                                            os.fsync(f.fileno())
                                        except Exception:
                                            pass
                                except Exception as e:
                                    print("[WARN] Error writing output:", e)
                                last_text = new_text
                        except Exception as e:
                            print("[WARN] Gesture classification write error:", e)
                        # draw text onto image buffer (useful for saved frames)
                        try:
                            cv2.putText(image, f"Gesture: {gesture}", (20, 50),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                        except Exception:
                            pass
                        # optional hardware control (ignored on errors)
                        try:
                            if gesture == "L": cnt.led(1)
                            elif gesture == "ThumbsUp": cnt.led(5)
                            elif gesture == "Peace": cnt.led(2)
                        except Exception:
                            pass

            # Display the camera feed with hand landmarks and gesture text
            cv2.imshow('Hand Gesture Recognition - Press Q to Quit', image)
            
            # Check for 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[INFO] User pressed 'q' - exiting.")
                break

            # write a JPEG frame for the frontend to stream (atomic write)
            try:
                tmp = FRAME_FILE + ".tmp"
                # prefer Pillow for robust JPEG writing; fallback to OpenCV
                try:
                    from PIL import Image
                    im = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
                    im.save(tmp, format='JPEG', quality=85)
                except Exception:
                    # fallback to cv2.imwrite
                    cv2.imwrite(tmp, image)
                try:
                    os.replace(tmp, FRAME_FILE)
                except Exception:
                    os.rename(tmp, FRAME_FILE)
            except Exception as e:
                print("[WARN] Failed to write frame:", e)

finally:
    try: video.release()
    except Exception: pass
    try: cv2.destroyAllWindows()
    except Exception: pass
    try: cnt.cleanup()
    except Exception: pass
    print("[INFO] Hand gestures script exiting.")