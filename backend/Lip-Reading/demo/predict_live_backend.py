import os
import cv2
import dlib
import math
import json
import statistics
from PIL import Image
import imageio.v2 as imageio
import numpy as np
import csv
from collections import deque
import tensorflow as tf
import sys
import time

# Add data directory to path
sys.path.append('../data_collection')
# We need to make sure we can import from data.constants
# The script is in backend/Lip-Reading/demo/
# constants.py is in backend/Lip-Reading/data/
# So ../data is correct.

try:
    from constants import *
    from constants import TOTAL_FRAMES, VALID_WORD_THRESHOLD, NOT_TALKING_THRESHOLD, PAST_BUFFER_SIZE, LIP_WIDTH, LIP_HEIGHT
except ImportError:
    # Fallback if running from a different CWD
    sys.path.append(os.path.join(os.path.dirname(__file__), '../data_collection'))
    from constants import *
    from constants import TOTAL_FRAMES, VALID_WORD_THRESHOLD, NOT_TALKING_THRESHOLD, PAST_BUFFER_SIZE, LIP_WIDTH, LIP_HEIGHT

# -----------------------------------------------------------------------------
# SETUP PATHS FOR I/O
# -----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/Lip-Reading
OUTPUT_FILE = os.path.join(BASE_DIR, "output.txt")
STOP_FILE = os.path.join(BASE_DIR, "stop.txt")
FRAME_FILE = os.path.join(BASE_DIR, "frame.jpg")
MODEL_WEIGHTS = os.path.join(BASE_DIR, "model", "model_weights.h5")
FACE_WEIGHTS = os.path.join(BASE_DIR, "model", "face_weights.dat")

print(f"[BACKEND] Starting Lip Reading Backend...", flush=True)
print(f"[BACKEND] Output: {OUTPUT_FILE}", flush=True)
print(f"[BACKEND] Stop: {STOP_FILE}", flush=True)
print(f"[BACKEND] Frame: {FRAME_FILE}", flush=True)

# -----------------------------------------------------------------------------
# MODEL SETUP
# -----------------------------------------------------------------------------
label_dict = {
    6: 'hello', 5: 'dog', 10: 'my', 12: 'you', 9: 'lips', 3: 'cat', 
    11: 'read', 0: 'a', 4: 'demo', 7: 'here', 8: 'is', 1: 'bye', 2: 'can'
}

# Define the input shape
input_shape = (TOTAL_FRAMES, 80, 112, 3)

# Define the model architecture
model = tf.keras.Sequential([
    tf.keras.layers.Conv3D(16, (3, 3, 3), activation='relu', input_shape=input_shape),
    tf.keras.layers.MaxPooling3D((2, 2, 2)),
    tf.keras.layers.Conv3D(64, (3, 3, 3), activation='relu'),
    tf.keras.layers.MaxPooling3D((2, 2, 2)),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(len(label_dict), activation='softmax')
])

print(f"[BACKEND] Loading weights from {MODEL_WEIGHTS}", flush=True)
if os.path.exists(MODEL_WEIGHTS):
    model.load_weights(MODEL_WEIGHTS, by_name=True)
else:
    print(f"[ERROR] Model weights not found at {MODEL_WEIGHTS}", flush=True)
    sys.exit(1)

# Load the detector
detector = dlib.get_frontal_face_detector()

# Load the predictor
print(f"[BACKEND] Loading face predictor from {FACE_WEIGHTS}", flush=True)
if os.path.exists(FACE_WEIGHTS):
    predictor = dlib.shape_predictor(FACE_WEIGHTS)
else:
    print(f"[ERROR] Face weights not found at {FACE_WEIGHTS}", flush=True)
    sys.exit(1)

# -----------------------------------------------------------------------------
# MAIN LOOP
# -----------------------------------------------------------------------------
def main():
    # Try different camera indices
    cap = None
    for i in range(2):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[BACKEND] Opened camera index {i}", flush=True)
            break
        cap = None
    
    if cap is None:
        print("[ERROR] Could not open any camera.", flush=True)
        return

    curr_word_frames = []
    not_talking_counter = 0
    past_word_frames = deque(maxlen=PAST_BUFFER_SIZE)
    spoken_already = []
    
    predicted_word_label = None
    draw_prediction = False
    count = 0

    print("[BACKEND] Loop starting...", flush=True)

    while True:
        # 1. CHECK STOP SIGNAL
        if os.path.exists(STOP_FILE):
             print("[BACKEND] Stop file detected. Exiting...", flush=True)
             break

        # 2. READ FRAME
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Failed to read frame", flush=True)
            time.sleep(0.1)
            continue
        
        # 3. PROCESSING
        gray = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        is_talking_now = False

        for face in faces:
            landmarks = predictor(image=gray, box=face)

            # Mouth landmarks
            mouth_top = (landmarks.part(51).x, landmarks.part(51).y)
            mouth_bottom = (landmarks.part(57).x, landmarks.part(57).y)
            lip_distance = math.hypot(mouth_bottom[0] - mouth_top[0], mouth_bottom[1] - mouth_top[1])

            # Lip region extraction logic
            lip_left = landmarks.part(48).x
            lip_right = landmarks.part(54).x
            lip_top = landmarks.part(50).y
            lip_bottom = landmarks.part(58).y

            width_diff = LIP_WIDTH - (lip_right - lip_left)
            height_diff = LIP_HEIGHT - (lip_bottom - lip_top)
            pad_left = width_diff // 2
            pad_right = width_diff - pad_left
            pad_top = height_diff // 2
            pad_bottom = height_diff - pad_top

            pad_left = min(pad_left, lip_left)
            pad_right = min(pad_right, frame.shape[1] - lip_right)
            pad_top = min(pad_top, lip_top)
            pad_bottom = min(pad_bottom, frame.shape[0] - lip_bottom)

            lip_frame = frame[lip_top - pad_top:lip_bottom + pad_bottom, lip_left - pad_left:lip_right + pad_right]
            
            # Additional check to ensure valid resize
            if lip_frame.size == 0:
                continue

            lip_frame = cv2.resize(lip_frame, (LIP_WIDTH, LIP_HEIGHT))
            
            # Image enhancement (LAB contrast + CLAHE + Blur)
            lip_frame_lab = cv2.cvtColor(lip_frame, cv2.COLOR_BGR2LAB)
            l_channel, a_channel, b_channel = cv2.split(lip_frame_lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(3,3))
            l_channel_eq = clahe.apply(l_channel)
            lip_frame_eq = cv2.merge((l_channel_eq, a_channel, b_channel))
            lip_frame_eq = cv2.cvtColor(lip_frame_eq, cv2.COLOR_LAB2BGR)
            lip_frame_eq = cv2.GaussianBlur(lip_frame_eq, (7, 7), 0)
            lip_frame_eq = cv2.bilateralFilter(lip_frame_eq, 5, 75, 75)
            kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
            lip_frame_eq = cv2.filter2D(lip_frame_eq, -1, kernel)
            lip_frame_eq = cv2.GaussianBlur(lip_frame_eq, (5, 5), 0)
            lip_frame = lip_frame_eq

            # Visual Feedback on Frame
            for n in range(48, 61):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(img=frame, center=(x, y), radius=3, color=(0, 255, 0), thickness=-1)

            # TALKING LOGIC
            if lip_distance > 45: # person is talking
                is_talking_now = True
                cv2.putText(frame, "Talking", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                curr_word_frames.append(lip_frame.tolist())
                not_talking_counter = 0
                draw_prediction = False
            else:
                cv2.putText(frame, "Not talking", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                not_talking_counter += 1

                # PREDICTION LOGIC
                if not_talking_counter >= NOT_TALKING_THRESHOLD and len(curr_word_frames) + PAST_BUFFER_SIZE == TOTAL_FRAMES:
                    
                    curr_word_frames = list(past_word_frames) + curr_word_frames
                    curr_data = np.array([curr_word_frames[:input_shape[0]]])
                    
                    print(f"[BACKEND] Predicting shape: {curr_data.shape}", flush=True)

                    prediction = model.predict(curr_data)
                    
                    predicted_class_index = np.argmax(prediction)
                    # Simple loop to avoid repeating immediately same word if needed, 
                    # but original logic just checks spoken_already.
                    # Adapting original logic:
                    while label_dict[predicted_class_index] in spoken_already:
                         prediction[0][predicted_class_index] = 0
                         predicted_class_index = np.argmax(prediction)
                    
                    predicted_word_label = label_dict[predicted_class_index]
                    spoken_already.append(predicted_word_label)
                    
                    print(f"[BACKEND] PREDICTION: {predicted_word_label}", flush=True)
                    
                    # WRITE RESULT TO FILE
                    try:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            f.write(predicted_word_label)
                    except Exception as e:
                        print(f"[ERROR] writing output: {e}", flush=True)

                    draw_prediction = True
                    count = 0
                    curr_word_frames = []
                    not_talking_counter = 0
                
                elif not_talking_counter < NOT_TALKING_THRESHOLD and len(curr_word_frames) + PAST_BUFFER_SIZE < TOTAL_FRAMES and len(curr_word_frames) > VALID_WORD_THRESHOLD:
                    curr_word_frames.append(lip_frame.tolist())
                    not_talking_counter = 0
                
                elif len(curr_word_frames) < VALID_WORD_THRESHOLD or (not_talking_counter >= NOT_TALKING_THRESHOLD and len(curr_word_frames) + PAST_BUFFER_SIZE > TOTAL_FRAMES):
                    curr_word_frames = []

            past_word_frames.append(lip_frame.tolist())

        # Draw Prediction on screen (persists for a few frames)
        if draw_prediction and count < 20:
            count += 1
            cv2.putText(frame, predicted_word_label, (50 ,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 2)
        elif count >= 20:
            draw_prediction = False

        # 4. WRITE FRAME TO FILE
        # Use a temp file to avoid tearing/half-written reads only if critical, 
        # but for simple MJPEG streaming, direct write is often 'okay' enough or we use rename.
        # Win32 rename is atomic-ish.
        try:
            tmp_frame = FRAME_FILE + ".tmp.jpg"
            cv2.imwrite(tmp_frame, frame)
            # Atomic replace
            try:
                os.replace(tmp_frame, FRAME_FILE)
            except Exception:
                # Fallback for windows permission issues sometimes
                if os.path.exists(FRAME_FILE):
                    os.remove(FRAME_FILE)
                os.rename(tmp_frame, FRAME_FILE)
        except Exception as e:
            print(f"[ERROR] Failed to write frame: {e}", flush=True)

        # Throttle loop slightly
        time.sleep(0.01)

    cap.release()
    print("[BACKEND] Exiting Lip Reading...", flush=True)

if __name__ == "__main__":
    main()
