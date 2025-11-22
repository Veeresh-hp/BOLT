import cv2
import numpy as np
import tensorflow as tf
import dlib
import os
import time
from deep_translator import GoogleTranslator

# Paths
THIS_DIR = os.path.dirname(__file__)  # .../lip reading/src
PARENT_DIR = os.path.dirname(THIS_DIR)  # .../lip reading
MODEL_PATH = os.path.join(THIS_DIR, "model", "lip_reader_cnn_lstm.h5")
PROCESSED_DATA_DIR = os.path.join(THIS_DIR, "processed_data")
OUTPUT_FILE = os.path.join(PARENT_DIR, "output.txt")
STOP_FILE = os.path.join(PARENT_DIR, "stop.txt")

TRANSLATE_DEST = 'kn'
translator = GoogleTranslator(source='auto', target=TRANSLATE_DEST)

if not os.path.exists(MODEL_PATH):
    print(f"Error: Model file {MODEL_PATH} not found.")
    exit(1)

model = tf.keras.models.load_model(MODEL_PATH)
print(f"\n✅ Loaded model from {MODEL_PATH}")

if not os.path.exists(PROCESSED_DATA_DIR):
    print(f"Error: Processed data dir {PROCESSED_DATA_DIR} not found.")
    exit(1)

words = sorted(os.listdir(PROCESSED_DATA_DIR))
if not words:
    print("Error: No words found in processed_data/.")
    exit(1)

word_to_index = {word: i for i, word in enumerate(words)}
index_to_word = {i: word for word, i in word_to_index.items()}
print("Loaded words:", words)

detector = dlib.get_frontal_face_detector()
predictor_path = os.path.join(THIS_DIR, "..", "model", "shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(predictor_path)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

FRAME_COUNT = 22
MOVEMENT_THRESHOLD = 1500

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit(1)

# track frames for prediction
frames = []
recording = False
predicted_word = ""
prev_lip_region = None

# last written output to avoid noisy writes
last_text = ""

frame_file = os.path.join(PARENT_DIR, "frame.jpg")

while True:
    # check stop signal
    if os.path.exists(STOP_FILE):
        print("[INFO] Stop file found - exiting lip reading loop.")
        break

    ret, frame = cap.read()
    if not ret:
        time.sleep(0.1)
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 1)

    if len(faces) == 0:
        faces_opencv = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=3)
        if len(faces_opencv) > 0:
            (x, y, w, h) = faces_opencv[0]
            x_min, x_max = x, x + w
            y_min, y_max = y + int(h * 0.6), y + h
            faces = [dlib.rectangle(x_min, y_min, x_max, y_max)]
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)

    if len(faces) > 0:
        face = faces[0]
        landmarks = predictor(gray, face)

        x_min = min([landmarks.part(i).x for i in range(48, 68)])
        x_max = max([landmarks.part(i).x for i in range(48, 68)])
        y_min = min([landmarks.part(i).y for i in range(48, 68)])
        y_max = max([landmarks.part(i).y for i in range(48, 68)])

        x_min = max(0, x_min - 10)
        x_max = min(frame.shape[1], x_max + 10)
        y_min = max(0, y_min - 10)
        y_max = min(frame.shape[0], y_max + 10)

        box_width = x_max - x_min
        box_height = y_max - y_min
        if box_width > box_height:
            center_y = (y_min + y_max) // 2
            y_min = max(0, center_y - box_width // 2)
            y_max = min(frame.shape[0], center_y + box_width // 2)
        else:
            center_x = (x_min + x_max) // 2
            x_min = max(0, center_x - box_height // 2)
            x_max = min(frame.shape[1], center_x + box_height // 2)

        lip_region = frame[y_min:y_max, x_min:x_max]
        lip_region = cv2.resize(lip_region, (112, 80))
        gray_lip = cv2.cvtColor(lip_region, cv2.COLOR_BGR2GRAY)

        lip_moving = False
        if prev_lip_region is not None:
            diff = np.sum(np.abs(gray_lip - prev_lip_region))
            if diff > MOVEMENT_THRESHOLD:
                lip_moving = True
        prev_lip_region = gray_lip.copy()

        blurred = cv2.GaussianBlur(gray_lip, (5, 5), 0)
        min_pixel = np.min(blurred)
        max_pixel = np.max(blurred)
        contrast_stretched = (blurred - min_pixel) / (max_pixel - min_pixel + 1e-5) * 255
        contrast_stretched = contrast_stretched.astype(np.uint8)
        bilateral_filtered = cv2.bilateralFilter(contrast_stretched, 5, 75, 75)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(bilateral_filtered, -1, sharpen_kernel)
        final_processed = cv2.GaussianBlur(sharpened, (3, 3), 0)
        normalized = final_processed / 255.0

        # automatic recording trigger: start when lips move
        if lip_moving and not recording:
            recording = True
            frames = []
        if recording:
            frames.append(normalized)

        if recording and len(frames) == FRAME_COUNT:
            try:
                input_sequence = np.array(frames, dtype=np.float32)
                input_sequence = np.expand_dims(input_sequence, axis=0)
                input_sequence = np.expand_dims(input_sequence, axis=-1)
                prediction = model.predict(input_sequence)
                predicted_index = np.argmax(prediction)
                predicted_word = index_to_word[predicted_index]
                try:
                    translated = translator.translate(predicted_word)
                except Exception:
                    translated = "[Translation error]"

                # write output only on change
                try:
                    os.makedirs(PARENT_DIR, exist_ok=True)
                    new_text = f"Predicted: {predicted_word}\nTranslated: {translated}"
                    if new_text != last_text:
                        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                            f.write(new_text)
                            f.flush()
                            try:
                                os.fsync(f.fileno())
                            except Exception:
                                pass
                        last_text = new_text
                except Exception as e:
                    print("[WARN] Error writing output file:", e)

                frames = []
                recording = False
            except Exception as e:
                print("[WARN] Prediction error:", e)
    else:
        prev_lip_region = None

    # draw prediction text onto frame for saved frame
    if predicted_word:
        try:
            cv2.putText(frame, f"Predicted: {predicted_word}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            try:
                translated
            except NameError:
                translated = ""
            cv2.putText(frame, f"Translated: {translated}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 140, 255), 2, cv2.LINE_AA)
        except Exception:
            pass

    # write a preview frame for the frontend (atomic)
    try:
        tmp = frame_file + ".tmp"
        cv2.imwrite(tmp, frame)
        try:
            os.replace(tmp, frame_file)
        except Exception:
            os.rename(tmp, frame_file)
    except Exception:
        pass

# cleanup
cap.release()
print("[INFO] Lip reading script exiting.")
