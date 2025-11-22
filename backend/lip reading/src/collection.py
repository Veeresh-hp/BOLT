import cv2
import dlib
import os
import time
import numpy as np
from datetime import datetime
import json
import threading
from collections import deque
import argparse
import sys

class EnhancedDataCollector:
    def __init__(self):
        """Initialize the enhanced data collection system"""
        # Configuration
        self.OUTPUT_DIR = "enhanced_data/"
        self.FRAMES_PER_WORD = 22
        self.MOVEMENT_THRESHOLD = 1200
        self.MIN_RECORDING_INTERVAL = 2.0  # Seconds between recordings
        self.QUALITY_THRESHOLD = 0.7  # Quality score threshold
        
        # UI Configuration
        self.UI_CONFIG = {
            'bg_color': (30, 30, 30),
            'text_color': (255, 255, 255),
            'accent_color': (0, 255, 150),
            'warning_color': (0, 165, 255),
            'error_color': (0, 0, 255),
            'recording_color': (0, 0, 255),
            'font_scale': 0.6,
            'font_thickness': 2,
            'font': cv2.FONT_HERSHEY_SIMPLEX
        }
        
        # State variables
        self.current_word = ""
        self.recording = False
        self.frame_count = 0
        self.take_number = 1
        self.auto_mode = False
        self.preview_mode = False
        self.total_takes = 0
        self.session_stats = {'successful_takes': 0, 'failed_takes': 0, 'words_collected': set()}
        
        # Quality control
        self.prev_lip_regions = deque(maxlen=5)
        self.movement_history = deque(maxlen=10)
        self.last_recording_time = 0
        self.current_take_frames = []
        self.quality_scores = []
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        
        # Initialize components
        self._setup_face_detection()
        self._setup_directories()
        
    def _setup_face_detection(self):
        """Initialize face detection components"""
        try:
            # Dlib components
            self.detector = dlib.get_frontal_face_detector()
            predictor_path = "../model/shape_predictor_68_face_landmarks.dat"
            if not os.path.exists(predictor_path):
                raise FileNotFoundError(f"Landmark predictor {predictor_path} not found.")
            self.predictor = dlib.shape_predictor(predictor_path)
            
            # OpenCV cascade (fallback)
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            print("✅ Face detection components initialized")
            
        except Exception as e:
            print(f"❌ Error setting up face detection: {e}")
            sys.exit(1)
    
    def _setup_directories(self):
        """Setup directory structure"""
        if not os.path.exists(self.OUTPUT_DIR):
            os.makedirs(self.OUTPUT_DIR)
            
        # Create metadata directory
        self.metadata_dir = os.path.join(self.OUTPUT_DIR, "metadata")
        if not os.path.exists(self.metadata_dir):
            os.makedirs(self.metadata_dir)
            
        print(f"📁 Data will be saved to: {self.OUTPUT_DIR}")
    
    def _get_word_input(self):
        """Get word input with validation"""
        while True:
            word = input("\n📝 Enter the word to record (or 'quit' to exit): ").strip().lower()
            if word == 'quit':
                return None
            if word and word.isalpha():
                return word
            print("⚠ Please enter a valid word containing only letters.")
    
    def _calculate_quality_score(self, lip_region, landmarks=None):
        """Calculate quality score for the current frame"""
        if lip_region is None or lip_region.size == 0:
            return 0.0
            
        quality_factors = []
        
        # 1. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(lip_region, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 1000.0, 1.0)  # Normalize
        quality_factors.append(sharpness_score * 0.3)
        
        # 2. Contrast (standard deviation)
        contrast_score = np.std(lip_region) / 128.0  # Normalize to [0,1]
        quality_factors.append(contrast_score * 0.2)
        
        # 3. Brightness consistency (not too dark or too bright)
        mean_brightness = np.mean(lip_region)
        brightness_score = 1.0 - abs(mean_brightness - 127.5) / 127.5
        quality_factors.append(brightness_score * 0.2)
        
        # 4. Size adequacy
        size_score = min(lip_region.shape[0] * lip_region.shape[1] / (80 * 112), 1.0)
        quality_factors.append(size_score * 0.1)
        
        # 5. Movement consistency (if we have history)
        if len(self.movement_history) > 2:
            movement_variance = np.var(list(self.movement_history))
            movement_score = max(0, 1.0 - movement_variance / 10000.0)
            quality_factors.append(movement_score * 0.2)
        else:
            quality_factors.append(0.2)  # Default score
        
        return sum(quality_factors)
    
    def _advanced_preprocessing(self, lip_region):
        """Enhanced preprocessing for better quality assessment"""
        if lip_region is None or lip_region.size == 0:
            return None
            
        # Apply gentle denoising
        denoised = cv2.bilateralFilter(lip_region, 5, 50, 50)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
        enhanced = clahe.apply(denoised)
        
        return enhanced
    
    def _extract_lip_region_enhanced(self, frame, landmarks):
        """Enhanced lip region extraction with quality assessment"""
        # Get lip landmarks (points 48-67)
        lip_points = np.array([[landmarks.part(i).x, landmarks.part(i).y] for i in range(48, 68)])
        
        # Calculate bounding box
        x_min, y_min = np.min(lip_points, axis=0)
        x_max, y_max = np.max(lip_points, axis=0)
        
        # Dynamic expansion based on lip size
        lip_width = x_max - x_min
        lip_height = y_max - y_min
        
        # Adaptive margins (25-40% depending on size)
        margin_ratio = max(0.25, min(0.4, 50 / max(lip_width, lip_height)))
        margin_x = int(lip_width * margin_ratio)
        margin_y = int(lip_height * (margin_ratio + 0.1))
        
        # Apply margins with bounds checking
        x_min = max(0, x_min - margin_x)
        x_max = min(frame.shape[1], x_max + margin_x)
        y_min = max(0, y_min - margin_y)
        y_max = min(frame.shape[0], y_max + margin_y)
        
        # Ensure minimum size
        min_size = 60
        if (x_max - x_min) < min_size or (y_max - y_min) < min_size:
            return None, None, 0.0
        
        # Extract region
        if len(frame.shape) == 3:
            lip_region_color = frame[y_min:y_max, x_min:x_max]
            lip_region_gray = cv2.cvtColor(lip_region_color, cv2.COLOR_BGR2GRAY)
        else:
            lip_region_gray = frame[y_min:y_max, x_min:x_max]
            lip_region_color = cv2.cvtColor(lip_region_gray, cv2.COLOR_GRAY2BGR)
        
        # Resize with high-quality interpolation
        if lip_region_color.size > 0:
            lip_region_color = cv2.resize(lip_region_color, (112, 80), 
                                          interpolation=cv2.INTER_CUBIC)
            lip_region_gray = cv2.resize(lip_region_gray, (112, 80), 
                                       interpolation=cv2.INTER_CUBIC)
        
        # Calculate quality score
        enhanced_gray = self._advanced_preprocessing(lip_region_gray)
        quality_score = self._calculate_quality_score(enhanced_gray, landmarks)
        
        return lip_region_color, (x_min, y_min, x_max, y_max), quality_score
    
    def _detect_speech_activity(self, current_lip_gray):
        """Enhanced speech activity detection"""
        if len(self.prev_lip_regions) == 0:
            return False
            
        # Calculate movement from multiple previous frames
        movements = []
        for prev_lip in list(self.prev_lip_regions)[-3:]:  # Use last 3 frames
            if prev_lip is not None:
                # Structural similarity approach
                diff = cv2.absdiff(current_lip_gray, prev_lip)
                movement = np.sum(diff)
                movements.append(movement)
        
        if not movements:
            return False
        
        current_movement = np.mean(movements)
        self.movement_history.append(current_movement)
        
        # Dynamic threshold based on recent movement history
        if len(self.movement_history) > 5:
            baseline = np.percentile(list(self.movement_history), 30)
            dynamic_threshold = max(self.MOVEMENT_THRESHOLD, baseline * 1.5)
        else:
            dynamic_threshold = self.MOVEMENT_THRESHOLD
        
        # Check if movement is significant and consistent
        is_moving = current_movement > dynamic_threshold
        
        # Additional check for sustained movement (avoid false triggers)
        if len(self.movement_history) >= 3:
            recent_movements = list(self.movement_history)[-3:]
            sustained_movement = sum(1 for m in recent_movements if m > dynamic_threshold) >= 2
            return is_moving and sustained_movement
        
        return is_moving
    
    def _save_take_metadata(self, take_dir, quality_scores, timestamps):
        """Save metadata for the recorded take"""
        metadata = {
            'word': self.current_word,
            'take_number': self.take_number,
            'timestamp': datetime.now().isoformat(),
            'frame_count': len(quality_scores),
            'quality_scores': quality_scores,
            'average_quality': np.mean(quality_scores),
            'min_quality': np.min(quality_scores),
            'max_quality': np.max(quality_scores),
            'timestamps': timestamps,
            'fps': self.current_fps,
            'movement_threshold': self.MOVEMENT_THRESHOLD
        }
        
        metadata_path = os.path.join(take_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata
    
    def _calculate_fps(self):
        """Calculate current FPS"""
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.fps_start_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def _draw_enhanced_ui(self, frame, lip_bbox=None, quality_score=0.0, movement_detected=False):
        """Draw comprehensive UI overlay"""
        height, width = frame.shape[:2]
        
        # Create info panel
        panel_height = 150
        panel = np.full((panel_height, width, 3), self.UI_CONFIG['bg_color'], dtype=np.uint8)
        
        # Title
        title = f"Enhanced Data Collector - Word: '{self.current_word.upper()}'"
        cv2.putText(panel, title, (10, 25), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'], self.UI_CONFIG['accent_color'], 
                    self.UI_CONFIG['font_thickness'])
        
        # Status line
        status_y = 45
        if self.recording:
            progress = f"{self.frame_count}/{self.FRAMES_PER_WORD}"
            status = f"🔴 RECORDING {progress} | Take: {self.take_number}"
            color = self.UI_CONFIG['recording_color']
        elif self.auto_mode:
            status = "🟡 AUTO MODE - Speak to trigger recording"
            color = self.UI_CONFIG['warning_color']
        else:
            status = "⚪ MANUAL MODE - Press 'R' to record"
            color = self.UI_CONFIG['text_color']
        
        cv2.putText(panel, status, (10, status_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'], color, self.UI_CONFIG['font_thickness'])
        
        # Statistics
        stats_y = 65
        stats = f"Takes: {self.take_number-1} | Session: {self.session_stats['successful_takes']} successful"
        cv2.putText(panel, stats, (10, stats_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'] - 0.1, self.UI_CONFIG['text_color'], 
                    self.UI_CONFIG['font_thickness'] - 1)
        
        # Quality indicators
        quality_y = 85
        quality_text = f"Quality: {quality_score:.2f}"
        quality_color = self.UI_CONFIG['accent_color'] if quality_score > self.QUALITY_THRESHOLD else self.UI_CONFIG['warning_color']
        cv2.putText(panel, quality_text, (10, quality_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'], quality_color, self.UI_CONFIG['font_thickness'])
        
        # Movement indicator
        movement_text = "Movement: YES" if movement_detected else "Movement: NO"
        movement_color = self.UI_CONFIG['accent_color'] if movement_detected else self.UI_CONFIG['text_color']
        cv2.putText(panel, movement_text, (200, quality_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'], movement_color, self.UI_CONFIG['font_thickness'])
        
        # FPS
        fps_text = f"FPS: {self.current_fps:.1f}"
        cv2.putText(panel, fps_text, (width - 120, quality_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'], self.UI_CONFIG['text_color'], 
                    self.UI_CONFIG['font_thickness'])
        
        # Controls
        controls_y = 110
        if self.auto_mode:
            controls = "Controls: 'M'=Manual | 'N'=New Word | 'P'=Preview | 'Q'=Quit"
        else:
            controls = "Controls: 'R'=Record | 'A'=Auto Mode | 'N'=New Word | 'P'=Preview | 'Q'=Quit"
        
        cv2.putText(panel, controls, (10, controls_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'] - 0.1, self.UI_CONFIG['text_color'], 
                    self.UI_CONFIG['font_thickness'] - 1)
        
        # Tips
        tips_y = 130
        tip_text = "Tips: Good lighting, clear speech, steady head position"
        cv2.putText(panel, tip_text, (10, tips_y), self.UI_CONFIG['font'], 
                    self.UI_CONFIG['font_scale'] - 0.2, self.UI_CONFIG['text_color'], 
                    self.UI_CONFIG['font_thickness'] - 1)
        
        # Combine with frame
        combined = np.vstack([panel, frame])
        
        # Draw lip bounding box and quality indicator
        if lip_bbox is not None:
            x_min, y_min, x_max, y_max = lip_bbox
            y_min += panel_height  # Adjust for panel
            y_max += panel_height
            
            # Color based on quality
            if quality_score > self.QUALITY_THRESHOLD:
                box_color = self.UI_CONFIG['accent_color']
            else:
                box_color = self.UI_CONFIG['warning_color']
            
            cv2.rectangle(combined, (x_min, y_min), (x_max, y_max), box_color, 2)
            
            # Quality indicator circle
            circle_color = self.UI_CONFIG['accent_color'] if movement_detected else self.UI_CONFIG['text_color']
            cv2.circle(combined, (x_max + 15, y_min), 6, circle_color, -1)
        
        # Recording progress bar
        if self.recording:
            progress = self.frame_count / self.FRAMES_PER_WORD
            bar_width = 300
            bar_x = (combined.shape[1] - bar_width) // 2
            bar_y = combined.shape[0] - 40
            
            # Background
            cv2.rectangle(combined, (bar_x, bar_y), (bar_x + bar_width, bar_y + 25), 
                          self.UI_CONFIG['text_color'], 2)
            # Progress
            progress_width = int(bar_width * progress)
            cv2.rectangle(combined, (bar_x + 2, bar_y + 2), 
                          (bar_x + progress_width - 2, bar_y + 23), 
                          self.UI_CONFIG['accent_color'], -1)
            
            # Progress text
            progress_text = f"{self.frame_count}/{self.FRAMES_PER_WORD}"
            text_x = bar_x + bar_width // 2 - 30
            cv2.putText(combined, progress_text, (text_x, bar_y + 18), 
                        self.UI_CONFIG['font'], self.UI_CONFIG['font_scale'], 
                        self.UI_CONFIG['bg_color'], self.UI_CONFIG['font_thickness'])
        
        return combined
    
    def _show_preview_window(self):
        """Show preview of recorded takes"""
        if not hasattr(self, 'current_word') or not self.current_word:
            return
        
        word_dir = os.path.join(self.OUTPUT_DIR, self.current_word)
        if not os.path.exists(word_dir):
            return
        
        take_dirs = [d for d in os.listdir(word_dir) if d.startswith('take_')]
        if not take_dirs:
            return
        
        # Show the last take
        last_take = max(take_dirs, key=lambda x: int(x.split('_')[1]))
        take_path = os.path.join(word_dir, last_take)
        
        # Load frames
        frame_files = sorted([f for f in os.listdir(take_path) if f.endswith('.png')])
        if not frame_files:
            return
        
        print(f"\n🎬 Previewing {last_take} for word '{self.current_word}'")
        print("Press any key to advance frames, 'ESC' to close preview")
        
        for i, frame_file in enumerate(frame_files):
            frame_path = os.path.join(take_path, frame_file)
            frame = cv2.imread(frame_path)
            if frame is not None:
                # Resize for preview
                preview_frame = cv2.resize(frame, (224, 160))
                
                # Add frame info
                info_text = f"Frame {i+1}/{len(frame_files)} - {frame_file}"
                cv2.putText(preview_frame, info_text, (5, 15), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                
                cv2.imshow(f"Preview: {self.current_word} - {last_take}", preview_frame)
                
                key = cv2.waitKey(0) & 0xFF
                if key == 27:  # ESC key
                    break
        
        cv2.destroyWindow(f"Preview: {self.current_word} - {last_take}")
    
    def collect_data(self, word):
        """Main data collection loop for a specific word"""
        self.current_word = word
        self.take_number = 1
        
        # Setup word directory
        word_dir = os.path.join(self.OUTPUT_DIR, word)
        if not os.path.exists(word_dir):
            os.makedirs(word_dir)
        
        # Find next available take number
        existing_takes = [d for d in os.listdir(word_dir) if d.startswith('take_')]
        if existing_takes:
            max_take = max([int(t.split('_')[1]) for t in existing_takes])
            self.take_number = max_take + 1
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Error: Could not open webcam.")
            return False
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print(f"\n🎯 Collecting data for word: '{word}'")
        print("📋 Instructions:")
        print("   - Position face clearly in camera view")
        print("   - Ensure good lighting")
        print("   - Press 'R' to start manual recording")
        print("   - Press 'A' to enable auto-recording mode")
        print("   - Speak the word clearly when recording")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("⚠ Warning: Could not read frame.")
                    continue
                
                self._calculate_fps()
                
                # Flip for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.detector(gray, 1)
                
                # Fallback to OpenCV
                if len(faces) == 0:
                    faces_opencv = self.face_cascade.detectMultiScale(
                        gray, scaleFactor=1.05, minNeighbors=5, minSize=(120, 120)
                    )
                    if len(faces_opencv) > 0:
                        (x, y, w, h) = faces_opencv[0]
                        faces = [dlib.rectangle(x, y, x + w, y + h)]
                
                lip_bbox = None
                quality_score = 0.0
                movement_detected = False
                
                if len(faces) > 0:
                    # Process the largest face
                    face = max(faces, key=lambda f: f.width() * f.height())
                    landmarks = self.predictor(gray, face)
                    
                    # Extract lip region
                    lip_region_color, lip_bbox, quality_score = self._extract_lip_region_enhanced(frame, landmarks)
                    
                    if lip_region_color is not None:
                        lip_region_gray = cv2.cvtColor(lip_region_color, cv2.COLOR_BGR2GRAY)
                        
                        # Update previous regions
                        self.prev_lip_regions.append(lip_region_gray.copy())
                        
                        # Detect speech activity
                        movement_detected = self._detect_speech_activity(lip_region_gray)
                        
                        # Auto-recording logic
                        current_time = time.time()
                        if (self.auto_mode and not self.recording and 
                            movement_detected and 
                            current_time - self.last_recording_time > self.MIN_RECORDING_INTERVAL):
                            
                            print(f"\n🎬 Auto-recording triggered for '{word}' - Take {self.take_number}")
                            self.recording = True
                            self.frame_count = 0
                            self.current_take_frames = []
                            self.quality_scores = []
                            self.last_recording_time = current_time
                        
                        # --- CORRECTED RECORDING LOGIC ---
                        if self.recording and self.frame_count < self.FRAMES_PER_WORD:
                            # The faulty 'if' condition has been removed.
                            # The frame is now always added if a lip region is found.
                            self.current_take_frames.append({
                                'frame': lip_region_color.copy(),
                                'timestamp': time.time(),
                                'quality': quality_score
                            })
                            self.quality_scores.append(quality_score)
                            self.frame_count += 1
                            
                            # Complete recording
                            if self.frame_count == self.FRAMES_PER_WORD:
                                self._save_recording()
                else:
                    # No face detected
                    self.prev_lip_regions.clear()
                    self.movement_history.clear()
                
                # Draw UI
                display_frame = self._draw_enhanced_ui(frame, lip_bbox, quality_score, movement_detected)
                cv2.imshow(f"Enhanced Data Collector - {word}", display_frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r') and not self.recording and not self.auto_mode:
                    print(f"\n🎬 Manual recording started for '{word}' - Take {self.take_number}")
                    self.recording = True
                    self.frame_count = 0
                    self.current_take_frames = []
                    self.quality_scores = []
                elif key == ord('a') and not self.recording:
                    self.auto_mode = not self.auto_mode
                    mode = "enabled" if self.auto_mode else "disabled"
                    print(f"\n🤖 Auto-recording mode {mode}")
                elif key == ord('m'):
                    self.auto_mode = False
                    print("\n👤 Manual mode enabled")
                elif key == ord('n'):
                    print(f"\n📊 Session stats for '{word}':")
                    print(f"   Takes recorded: {self.take_number - 1}")
                    break  # Return to word selection
                elif key == ord('p'):
                    self._show_preview_window()
                elif key == ord('s'):  # Skip current recording
                    if self.recording:
                        print(f"\n⏭ Skipping current recording")
                        self.recording = False
                        self.frame_count = 0
                        self.current_take_frames = []
                        self.quality_scores = []
        
        except KeyboardInterrupt:
            print("\n⚠ Recording interrupted by user")
        except Exception as e:
            print(f"❌ Error during recording: {e}")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            
        return True

    def _save_recording(self):
        """Save the current recording with metadata"""
        if not self.current_take_frames:
            return
        
        # Create take directory
        take_dir = os.path.join(self.OUTPUT_DIR, self.current_word, f"take_{self.take_number}")
        os.makedirs(take_dir, exist_ok=True)
        
        # Save frames
        timestamps = []
        for i, frame_data in enumerate(self.current_take_frames):
            frame_path = os.path.join(take_dir, f"frame_{i:03d}.png")
            cv2.imwrite(frame_path, frame_data['frame'])
            timestamps.append(frame_data['timestamp'])
        
        # Save metadata
        avg_quality = np.mean(self.quality_scores) if self.quality_scores else 0.0
        self._save_take_metadata(take_dir, self.quality_scores, timestamps)
        
        # Update statistics
        if avg_quality > self.QUALITY_THRESHOLD:
            self.session_stats['successful_takes'] += 1
            status = "✅ HIGH QUALITY"
        else:
            self.session_stats['failed_takes'] += 1
            status = "⚠ LOW QUALITY"
        
        self.session_stats['words_collected'].add(self.current_word)
        
        print(f"\n{status} - Take {self.take_number} saved!")
        print(f"   📁 Location: {take_dir}")
        print(f"   📊 Quality: {avg_quality:.2f} (min: {np.min(self.quality_scores) if self.quality_scores else 0.0:.2f})")
        print(f"   🎬 Frames: {len(self.current_take_frames)}")
        
        # Reset for next recording
        self.recording = False
        self.frame_count = 0
        self.take_number += 1
        self.current_take_frames = []
        self.quality_scores = []
    
    def run(self):
        """Main application entry point"""
        print("🚀 Enhanced Lip Reading Data Collection System")
        print("=" * 50)
        
        try:
            while True:
                word = self._get_word_input()
                if word is None:
                    break
                
                self.collect_data(word)
                
                # Show session summary
                print(f"\n📊 Session Summary:")
                print(f"   Words collected: {len(self.session_stats['words_collected'])}")
                print(f"   Successful takes: {self.session_stats['successful_takes']}")
                print(f"   Total attempts: {self.session_stats['successful_takes'] + self.session_stats['failed_takes']}")
                
                continue_session = input("\n❓ Continue with another word? (y/n): ").strip().lower()
                if continue_session != 'y':
                    break
        
        except KeyboardInterrupt:
            print("\n👋 Session ended by user")
        finally:
            print("\n🏁 Data collection session completed!")
            print(f"📈 Final Statistics:")
            print(f"   Total words: {len(self.session_stats['words_collected'])}")
            print(f"   Successful takes: {self.session_stats['successful_takes']}")
            print(f"   Data saved to: {self.OUTPUT_DIR}")
            
            # Save session summary
            self._save_session_summary()

    def _save_session_summary(self):
        """Save session summary to file"""
        session_data = {
            'session_date': datetime.now().isoformat(),
            'words_collected': list(self.session_stats['words_collected']),
            'successful_takes': self.session_stats['successful_takes'],
            'failed_takes': self.session_stats['failed_takes'],
            'total_takes': self.session_stats['successful_takes'] + self.session_stats['failed_takes'],
            'collection_settings': {
                'frames_per_word': self.FRAMES_PER_WORD,
                'movement_threshold': self.MOVEMENT_THRESHOLD,
                'quality_threshold': self.QUALITY_THRESHOLD,
                'min_recording_interval': self.MIN_RECORDING_INTERVAL
            }
        }
        
        session_file = os.path.join(self.metadata_dir, f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        print(f"📋 Session summary saved to: {session_file}")

class DatasetValidator:
    """Utility class for validating collected dataset"""
    def __init__(self, data_dir):
        self.data_dir = data_dir
    
    def validate_dataset(self):
        """Validate the collected dataset"""
        print("\n🔍 Validating dataset...")
        
        if not os.path.exists(self.data_dir):
            print(f"❌ Data directory {self.data_dir} not found!")
            return False
        
        words = [d for d in os.listdir(self.data_dir) if os.path.isdir(os.path.join(self.data_dir, d)) and d != 'metadata']
        
        if not words:
            print("❌ No word directories found!")
            return False
        
        print(f"📚 Found {len(words)} words: {words}")
        
        total_takes = 0
        valid_takes = 0
        quality_scores = []
        
        for word in words:
            word_dir = os.path.join(self.data_dir, word)
            takes = [d for d in os.listdir(word_dir) if d.startswith('take_')]
            
            print(f"\n📝 Word: '{word}' - {len(takes)} takes")
            
            for take in takes:
                take_dir = os.path.join(word_dir, take)
                frames = [f for f in os.listdir(take_dir) if f.endswith('.png')]
                metadata_file = os.path.join(take_dir, 'metadata.json')
                
                total_takes += 1
                
                if len(frames) >= 20:  # Minimum frames threshold
                    valid_takes += 1
                    
                    # Load quality info if available
                    if os.path.exists(metadata_file):
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            quality_scores.append(metadata.get('average_quality', 0))
                
                status = "✅" if len(frames) >= 20 else "❌"
                print(f"   {status} {take}: {len(frames)} frames")
        
        print(f"\n📊 Dataset Summary:")
        print(f"   Total words: {len(words)}")
        print(f"   Total takes: {total_takes}")
        if total_takes > 0:
            print(f"   Valid takes: {valid_takes} ({valid_takes/total_takes*100:.1f}%)")
        else:
            print("   Valid takes: 0 (0.0%)")

        if quality_scores:
            print(f"   Average quality: {np.mean(quality_scores):.2f}")
            print(f"   Quality range: {np.min(quality_scores):.2f} - {np.max(quality_scores):.2f}")
        
        return valid_takes > 0

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Lip Reading Data Collection System')
    parser.add_argument('--validate', action='store_true', help='Validate existing dataset')
    parser.add_argument('--data-dir', default='data/', help='Data directory path')
    parser.add_argument('--frames', type=int, default=22, help='Frames per word')
    parser.add_argument('--threshold', type=int, default=1200, help='Movement threshold')
    parser.add_argument('--quality', type=float, default=0.7, help='Quality threshold')
    
    args = parser.parse_args()
    
    if args.validate:
        validator = DatasetValidator(args.data_dir)
        validator.validate_dataset()
        return
    
    # Create collector with custom parameters
    collector = EnhancedDataCollector()
    collector.OUTPUT_DIR = args.data_dir
    collector.FRAMES_PER_WORD = args.frames
    collector.MOVEMENT_THRESHOLD = args.threshold
    collector.QUALITY_THRESHOLD = args.quality
    
    # Setup directories with new path
    collector._setup_directories()
    
    print(f"🎯 Configuration:")
    print(f"   Data directory: {collector.OUTPUT_DIR}")
    print(f"   Frames per word: {collector.FRAMES_PER_WORD}")
    print(f"   Movement threshold: {collector.MOVEMENT_THRESHOLD}")
    print(f"   Quality threshold: {collector.QUALITY_THRESHOLD}")
    
    collector.run()

if __name__ == "__main__":
    main()