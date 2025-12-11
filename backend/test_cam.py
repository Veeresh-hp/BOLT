import cv2
import time

def test_camera(index, backend_name, backend_id):
    print(f"\nTesting Index {index} with {backend_name}...")
    try:
        cap = cv2.VideoCapture(index, backend_id)
        if not cap.isOpened():
            print(f"❌ Failed to open.")
            return False
        
        # Try to set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print(f"   Camera opened. Reading 10 frames...")
        success_count = 0
        for i in range(10):
            ret, frame = cap.read()
            if ret and frame is not None:
                success_count += 1
                if i == 0:
                    cv2.imwrite(f"test_cam_idx{index}_{backend_name}.jpg", frame)
            else:
                print(f"   Frame {i} read failed.")
            time.sleep(0.1)
        
        cap.release()
        
        if success_count > 0:
            print(f"✅ Success! Captured {success_count}/10 frames. Saved image.")
            return True
        else:
            print(f"❌ Opened but failed to read frames.")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

print("OpenCV Version:", cv2.__version__)
indices = [0, 1]
backends = [("ANY", cv2.CAP_ANY), ("DSHOW", cv2.CAP_DSHOW), ("MSMF", cv2.CAP_MSMF)]

results = {}
for idx in indices:
    for name, bid in backends:
        res = test_camera(idx, name, bid)
        results[(idx, name)] = res

print("\n--- Summary ---")
for (idx, name), success in results.items():
    status = "WORKING" if success else "FAILED"
    print(f"Index {idx} | {name}: {status}")
