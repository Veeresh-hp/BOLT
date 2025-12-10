"""
Data Collection Script for Hand Gestures
=========================================
This script helps you collect training data for new hand gestures.

Instructions:
1. Run this script
2. Enter the gesture name (e.g., "Hello", "Stop", "Okay")
3. Show the gesture to your camera
4. Press 's' to save samples (collect 20-50 samples per gesture)
5. Press 'q' to quit and move to next gesture
6. After collecting data for all gestures, train the model using train_gestures.py
"""

import cv2
import mediapipe as mp
import csv
import os

# Config
THIS_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(THIS_DIR, "gesture_data.csv")

# MediaPipe setup
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

def save_landmarks(label, lmList):
    """Save hand landmarks to CSV file."""
    file_exists = os.path.exists(DATA_FILE)
    
    with open(DATA_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        
        # Write header if file doesn't exist
        if not file_exists:
            header = ["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)]
            writer.writerow(header)
        
        # Validate we have 21 landmarks
        if len(lmList) != 21:
            print(f"[WARN] Skipped sample - expected 21 landmarks, got {len(lmList)}")
            return False
        
        # Save: label + x coordinates + y coordinates
        row = [label] + [p[1] for p in lmList] + [p[2] for p in lmList]
        writer.writerow(row)
        return True

def collect_gesture_data(gesture_name):
    """Collect training data for a specific gesture."""
    cap = cv2.VideoCapture(0)
    sample_count = 0
    
    print(f"\n{'='*60}")
    print(f"Collecting data for gesture: {gesture_name}")
    print(f"{'='*60}")
    print("Instructions:")
    print("  - Show your gesture to the camera")
    print("  - Press 's' to save a sample (collect 20-50 samples)")
    print("  - Press 'q' to finish this gesture and move to next")
    print(f"{'='*60}\n")
    
    with mp_hand.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7) as hands:
        while True:
            ret, image = cap.read()
            if not ret:
                print("[ERROR] Could not read from camera")
                break
            
            # Process image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = hands.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Extract landmarks
            lmList = []
            if results.multi_hand_landmarks:
                # Use first detected hand
                first_hand = results.multi_hand_landmarks[0]
                
                # Draw landmarks
                mp_draw.draw_landmarks(image, first_hand, mp_hand.HAND_CONNECTIONS)
                
                # Extract coordinates
                h, w, c = image.shape
                for id, lm in enumerate(first_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
            
            # Display info on screen
            status = "Hand Detected - Press 's' to save" if len(lmList) > 0 else "No Hand Detected"
            cv2.putText(image, f"Gesture: {gesture_name}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, f"Samples: {sample_count}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.putText(image, status, (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(image, "Press 'q' to finish", (10, 120),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('Gesture Data Collection', image)
            
            key = cv2.waitKey(1) & 0xFF
            
            # Save sample
            if key == ord('s') and len(lmList) == 21:
                if save_landmarks(gesture_name, lmList):
                    sample_count += 1
                    print(f"[INFO] Saved sample {sample_count} for '{gesture_name}'")
            
            # Quit this gesture
            elif key == ord('q'):
                break
    
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[SUCCESS] Collected {sample_count} samples for '{gesture_name}'\n")
    return sample_count

def main():
    """Main collection loop."""
    print("\n" + "="*60)
    print("HAND GESTURE DATA COLLECTION TOOL")
    print("="*60)
    print("\nThis tool helps you create training data for hand gestures.")
    print("You'll collect multiple samples for each gesture you want to recognize.")
    print("\nTips for good data:")
    print("  - Collect 20-50 samples per gesture")
    print("  - Vary hand position, angle, and distance slightly")
    print("  - Ensure good lighting")
    print("  - Keep hand in frame")
    print("="*60)
    
    # Check if data file exists
    if os.path.exists(DATA_FILE):
        print(f"\n[INFO] Existing data file found: {DATA_FILE}")
        response = input("Do you want to ADD to existing data? (y/n): ").strip().lower()
        if response != 'y':
            print("[INFO] Exiting. No data will be collected.")
            return
    
    # Collect data for multiple gestures
    while True:
        gesture_name = input("\nEnter gesture name (or 'done' to finish): ").strip()
        
        if gesture_name.lower() == 'done':
            break
        
        if not gesture_name:
            print("[ERROR] Gesture name cannot be empty")
            continue
        
        # Collect samples for this gesture
        sample_count = collect_gesture_data(gesture_name)
        
        if sample_count == 0:
            print("[WARN] No samples collected for this gesture")
    
    print("\n" + "="*60)
    print("DATA COLLECTION COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run 'python train_gestures.py' to train the model")
    print("2. Run 'python main.py' to test your gestures")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()