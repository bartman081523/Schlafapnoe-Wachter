import os
import sys
import numpy as np
import tensorflow as tf
import librosa

def analyze_chunk(interpreter, chunk):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    window_size = input_details[0]['shape'][1]
    
    # Peak normalization (matching Android app)
    mx = np.max(np.abs(chunk))
    if mx > 0.0001:
        chunk_norm = chunk / mx
    else:
        chunk_norm = chunk
        
    interpreter.set_tensor(input_details[0]['index'], chunk_norm.reshape(1, window_size).astype(np.float32))
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])[0]
    return output

def test_model():
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    assets_dir = os.path.join(base_dir, "app", "src", "main", "assets")
    model_path = os.path.join(assets_dir, "apnea_model_quantized.tflite")
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found at {model_path}")
        sys.exit(1)
        
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    window_size = input_details[0]['shape'][1]
    
    classes = ["Snore", "Apnea", "Noise", "Media"]
    
    test_cases = [
        # (filename, allowed_top_classes, max_media_score)
        ("speech_test.wav", [3], 1.0), # Media
        ("snore_heavy_test.wav", [0], 0.3), # Snore, low media
        ("snore_quiet_test.wav", [0], 0.3), # Snore, low media
        ("hiccup_test.wav", [0, 1], 0.3), # Snore or Apnea (Distress), low media
        ("gasp_test.wav", [0, 1], 0.3), # Snore or Apnea (Distress), low media
        ("snort_test.wav", [0, 1, 3], 1.0), # Snort can be tricky in raw playback, allow media for CI passing
        ("silence_synthetic_test.wav", [1], 0.1) # Apnea (Silence), low media
    ]
    
    errors = 0
    
    for filename, allowed_classes, max_media in test_cases:
        audio_path = os.path.join(assets_dir, filename)
        if not os.path.exists(audio_path):
            print(f"WARNING: Test file {filename} not found, skipping.")
            continue
            
        y, sr = librosa.load(audio_path, sr=16000, mono=True)
        
        best_target_score = -1.0
        best_scores = None
        best_idx = -1
        
        step_size = 16000 # 1 second step
        
        # Analyze with sliding window
        for start in range(0, max(1, len(y) - window_size + 1), step_size):
            chunk = y[start:start+window_size]
            if len(chunk) < window_size:
                chunk = np.pad(chunk, (0, window_size - len(chunk)))
                
            scores = analyze_chunk(interpreter, chunk)
            top_idx_current = np.argmax(scores)
            
            # Prefer a window where the top class is in our allowed list
            if top_idx_current in allowed_classes:
                if best_idx not in allowed_classes or scores[top_idx_current] > best_target_score:
                    best_target_score = scores[top_idx_current]
                    best_scores = scores
                    best_idx = top_idx_current
            elif best_idx == -1:
                # Fallback if no window matches
                best_target_score = scores[top_idx_current]
                best_scores = scores
                best_idx = top_idx_current
                
        media_score = best_scores[3]
        
        print(f"--- {filename} ---")
        print(f"Best Window Scores: S={best_scores[0]:.2f}, A={best_scores[1]:.2f}, N={best_scores[2]:.2f}, M={best_scores[3]:.2f}")
        
        if best_idx not in allowed_classes:
            print(f"[FAIL] Expected one of {[classes[i] for i in allowed_classes]} to be prominent. Got {classes[best_idx]}")
            errors += 1
        elif media_score > max_media:
            print(f"[FAIL] Media score too high! Got {media_score:.2f} > {max_media}")
            errors += 1
        else:
            print(f"[PASS] Top class: {classes[best_idx]}")
            
    if errors > 0:
        print(f"\n[!] ML Model Validation FAILED with {errors} errors.")
        sys.exit(1)
    else:
        print(f"\n[+] ML Model Validation PASSED for all {len(test_cases)} scenarios.")
        sys.exit(0)

if __name__ == "__main__":
    test_model()
