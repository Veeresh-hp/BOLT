"""
Train Hand Gesture Recognition Model
=====================================
This script trains a Random Forest classifier on collected gesture data.

Usage:
    python train_gestures.py

The script will:
1. Load data from gesture_data.csv
2. Clean and validate the dataset
3. Train a Random Forest model
4. Display accuracy and save the model
"""

import os
import csv
import shutil
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from collections import Counter

# Config
THIS_DIR = os.path.dirname(__file__)
DATA_FILE = os.path.join(THIS_DIR, "gesture_data.csv")
MODEL_FILE = os.path.join(THIS_DIR, "gesture_model.pkl")

def clean_dataset_file():
    """Clean the dataset file by fixing malformed rows."""
    if not os.path.exists(DATA_FILE):
        print("[ERROR] No data file found at:", DATA_FILE)
        return False
    
    tmp_rows = []
    kept, fixed, skipped = 0, 0, 0
    
    with open(DATA_FILE, newline="") as fin:
        reader = csv.reader(fin)
        try:
            header = next(reader)
        except StopIteration:
            print("[ERROR] Data file is empty")
            return False
        
        # Correct header
        correct_header = ["label"] + [f"x{i}" for i in range(21)] + [f"y{i}" for i in range(21)]
        tmp_rows.append(correct_header)
        
        for row in reader:
            n = len(row)
            if n == 43:  # Correct format: 1 label + 21 x + 21 y
                tmp_rows.append(row)
                kept += 1
            elif n == 85:  # Malformed: needs fixing
                label = row[0]
                xs = row[1:1+42][:21]
                ys = row[1+42:1+42+42][:21]
                fixed_row = [label] + xs + ys
                tmp_rows.append(fixed_row)
                fixed += 1
            else:
                skipped += 1
    
    # Backup original file
    try:
        shutil.copy2(DATA_FILE, DATA_FILE + ".bak")
        print(f"[INFO] Backup created: {DATA_FILE}.bak")
    except Exception as e:
        print(f"[WARN] Could not create backup: {e}")
    
    # Write cleaned data
    with open(DATA_FILE, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerows(tmp_rows)
    
    print(f"[INFO] Dataset cleaned: kept={kept}, fixed={fixed}, skipped={skipped}")
    return True

def analyze_dataset(df):
    """Display dataset statistics."""
    print("\n" + "="*60)
    print("DATASET ANALYSIS")
    print("="*60)
    print(f"Total samples: {len(df)}")
    print(f"Total features: {len(df.columns) - 1}")
    print(f"\nSamples per gesture:")
    
    label_counts = Counter(df['label'])
    for gesture, count in sorted(label_counts.items()):
        print(f"  {gesture:20s}: {count:3d} samples")
    
    print("\nRecommendations:")
    min_samples = min(label_counts.values())
    if min_samples < 20:
        print(f"  ⚠  Some gestures have < 20 samples. Collect more for better accuracy.")
    elif min_samples < 50:
        print(f"  ℹ  Good sample size. Consider collecting 50+ samples per gesture.")
    else:
        print(f"  ✓ Excellent sample size!")
    
    print("="*60 + "\n")

def train_model():
    """Train the gesture recognition model."""
    print("\n" + "="*60)
    print("TRAINING HAND GESTURE RECOGNITION MODEL")
    print("="*60 + "\n")
    
    # Check if data file exists
    if not os.path.exists(DATA_FILE):
        print("[ERROR] No training data found at:", DATA_FILE)
        print("\nPlease run 'python collect_data.py' first to collect training data.")
        return False
    
    # Clean dataset
    print("[STEP 1] Cleaning dataset...")
    if not clean_dataset_file():
        return False
    
    # Load data
    print("[STEP 2] Loading dataset...")
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception as e:
        print(f"[ERROR] Could not load data: {e}")
        return False
    
    # Analyze dataset
    analyze_dataset(df)
    
    # Prepare features and labels
    print("[STEP 3] Preparing features and labels...")
    X = df.drop("label", axis=1).values
    y = df["label"].values
    
    # Split data
    print("[STEP 4] Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"  Training samples: {len(X_train)}")
    print(f"  Testing samples: {len(X_test)}")
    
    # Train model
    print("\n[STEP 5] Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    print("[STEP 6] Evaluating model...")
    train_acc = model.score(X_train, y_train)
    test_acc = model.score(X_test, y_test)
    
    # Cross-validation
    print("[STEP 7] Performing cross-validation...")
    cv_scores = cross_val_score(model, X, y, cv=5)
    
    # Display results
    print("\n" + "="*60)
    print("TRAINING RESULTS")
    print("="*60)
    print(f"Training Accuracy:      {train_acc*100:.2f}%")
    print(f"Testing Accuracy:       {test_acc*100:.2f}%")
    print(f"Cross-validation (avg): {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
    print("="*60)
    
    # Check for overfitting
    if train_acc - test_acc > 0.1:
        print("\n⚠  Warning: Possible overfitting detected")
        print("   Consider collecting more diverse training data.")
    elif test_acc < 0.8:
        print("\n⚠  Warning: Low accuracy")
        print("   Consider collecting more samples or using more distinct gestures.")
    else:
        print("\n✓ Model trained successfully!")
    
    # Save model
    print(f"\n[STEP 8] Saving model to: {MODEL_FILE}")
    joblib.dump(model, MODEL_FILE)
    print("[SUCCESS] Model saved!\n")
    
    # Show gesture classes
    print("Recognized gestures:")
    for i, gesture in enumerate(sorted(set(y)), 1):
        print(f"  {i}. {gesture}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("1. Run 'python main.py' to test your gestures")
    print("2. To add more gestures, run 'python collect_data.py'")
    print("3. After adding data, run this script again to retrain")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        train_model()
    except KeyboardInterrupt:
        print("\n\n[INFO] Training interrupted by user.")
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
        import traceback
        traceback.print_exc()