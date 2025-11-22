import cv2
import os
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor

# --- Configuration ---
INPUT_DIR = "data/"
OUTPUT_DIR = "processed_data/"
EXPECTED_FRAMES = 22

def preprocess_image(image_path):
    """
    Applies the full preprocessing pipeline to a single image.
    """
    image = cv2.imread(image_path)
    if image is None:
        # This warning can be noisy in parallel, returning None is sufficient
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    min_pixel, max_pixel = np.min(blurred), np.max(blurred)
    if max_pixel == min_pixel: # Avoid division by zero
        return blurred.astype(np.uint8)

    contrast_stretched = ((blurred - min_pixel) / (max_pixel - min_pixel + 1e-6)) * 255
    contrast_stretched = contrast_stretched.astype(np.uint8)

    bilateral_filtered = cv2.bilateralFilter(contrast_stretched, 5, 75, 75)
    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(bilateral_filtered, -1, sharpen_kernel)
    
    return sharpened

def process_word(args):
    """
    Processes all takes for a given word. Accepts a tuple of arguments for multiprocessing.
    """
    word_path, word_output_path = args
    word_name = os.path.basename(word_path)

    takes = [d for d in os.listdir(word_path) if os.path.isdir(os.path.join(word_path, d))]
    if not takes:
        return f"Warning: No takes found in {word_path}."

    try:
        takes.sort(key=lambda x: int(x.split('_')[1]))
    except (ValueError, IndexError):
        takes.sort()

    for take in takes:
        take_path = os.path.join(word_path, take)
        frame_files = sorted([f for f in os.listdir(take_path) if f.endswith(('.png', '.jpg', '.jpeg'))])
        
        # ✨ FIX: Flexible frame handling to prevent data loss
        if len(frame_files) < EXPECTED_FRAMES:
            # Still skip takes that are too short
            continue
        
        if len(frame_files) > EXPECTED_FRAMES:
            # Truncate takes that are too long
            frame_files = frame_files[:EXPECTED_FRAMES]

        processed_frames = []
        for frame_file in frame_files:
            frame_path = os.path.join(take_path, frame_file)
            processed_frame = preprocess_image(frame_path)
            
            if processed_frame is None:
                processed_frames = [] # Invalidate the whole take
                break
            
            processed_frames.append(processed_frame)

        if len(processed_frames) == EXPECTED_FRAMES:
            final_array = np.array(processed_frames, dtype=np.float32) / 255.0
            npy_path = os.path.join(word_output_path, f"{take}.npy")
            np.save(npy_path, final_array)

    return f"Finished processing {word_name}."

def main():
    """
    Main function to run the preprocessing script in parallel.
    """
    if not os.path.exists(INPUT_DIR):
        print(f"Error: Input directory '{INPUT_DIR}' not found.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ✨ FIX: Filter out the 'metadata' directory
    words = sorted([
        d for d in os.listdir(INPUT_DIR)
        if os.path.isdir(os.path.join(INPUT_DIR, d)) and d != 'metadata'
    ])
    if not words:
        print(f"Error: No valid word directories found in '{INPUT_DIR}'.")
        return

    print(f"Starting parallel preprocessing of {len(words)} words...")
    
    # Prepare arguments for each process
    tasks = []
    for word in words:
        word_path = os.path.join(INPUT_DIR, word)
        word_output_path = os.path.join(OUTPUT_DIR, word)
        os.makedirs(word_output_path, exist_ok=True)
        tasks.append((word_path, word_output_path))

    # ✨ NEW: Use a process pool to execute tasks in parallel
    with ProcessPoolExecutor() as executor:
        # Use tqdm to create a progress bar for the parallel tasks
        results = list(tqdm(executor.map(process_word, tasks), total=len(tasks), desc="Overall Progress"))

    # Print any warnings or messages from the processes
    for result in results:
        if result and "Warning" in result:
            print(result)

    print(f"\n✅ Preprocessing complete! Processed data saved in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()