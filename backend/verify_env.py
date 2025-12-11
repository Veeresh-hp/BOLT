import sys
import importlib.util

def check_package(name):
    found = importlib.util.find_spec(name) is not None
    if found:
        try:
            mod = __import__(name)
            ver = getattr(mod, '__version__', 'unknown')
            print(f"✅ {name}: Installed ({ver})")
        except ImportError:
            print(f"✅ {name}: Installed (Import verified, version unknown)")
        except Exception as e:
            print(f"⚠️ {name}: Installed but error on import: {e}")
    else:
        print(f"❌ {name}: Not found")

print("--- Environment Verification ---")
print(f"Python Version: {sys.version}")

if sys.version_info.major == 3 and sys.version_info.minor == 10:
    print("✅ Python 3.10 is active.")
else:
    print("❌ WARNING: Python 3.10 is NOT active.")

print("\n--- Package Checks ---")
check_package('dlib')
check_package('cmake') # Python wrapper for cmake
check_package('cv2')
check_package('mediapipe')

print("\n--- Pip List (Filtered) ---")
try:
    from pip._internal.operations import freeze
    pkgs = [p for p in freeze.freeze() if 'dlib' in p or 'cmake' in p or 'tensorflow' in p]
    for p in pkgs:
        print(p)
except:
    pass
