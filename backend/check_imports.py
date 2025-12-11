import sys
try:
    print("Checking Flask...")
    import flask
    print(f"Flask {flask.__version__}")

    print("Checking OpenCV...")
    import cv2
    print(f"OpenCV {cv2.__version__}")

    print("Checking MediaPipe...")
    import mediapipe
    print(f"MediaPipe {mediapipe.__version__}")

    print("Checking TensorFlow...")
    import tensorflow as tf
    print(f"TensorFlow {tf.__version__}")

    print("Checking dlib...")
    import dlib
    print(f"dlib {dlib.__version__}")

    print("Checking pyfirmata...")
    import pyfirmata
    print("pyfirmata OK")
    
    print("\n✅ All critical imports successful!")
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    sys.exit(1)
