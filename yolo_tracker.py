import cv2
from ultralytics import YOLO
import time
import math
import itertools
from collections import deque
import numpy as np
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
from tensorflow.keras.models import load_model

print("Initializing YOLOv8 Spatial Engine...")
model = YOLO('yolov8n.pt') 

print("Loading Custom GRU Temporal Brain...")
try:
    temporal_brain = load_model('violence_temporal_brain.h5')
except Exception as e:
    print("ERROR: Could not find 'violence_temporal_brain.h5'.")
    exit()

# --- THE NEW VIDEO FILE ---
cap = cv2.VideoCapture('handshake.mp4')
prev_time = 0
frame_count = 0
FRAME_SKIP_INTERVAL = 3  

MIN_SAFE_DISTANCE = 150  
SEQUENCE_LENGTH = 30  

tracking_memory = {}
last_annotated_frame = None

print("\n[ACTIVE] X-Ray Debug Pipeline Live.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("End of video or video not found!")
        break
    frame = cv2.resize(frame, (1000, 600))

    frame_count += 1

    if frame_count % FRAME_SKIP_INTERVAL == 0 or last_annotated_frame is None:
        results = model.track(source=frame, persist=True, classes=[0], verbose=False)
        last_annotated_frame = results[0].plot()

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.cpu().numpy().astype(int)
            active_centroids = {}

            for box, track_id in zip(boxes, track_ids):
                x1, y1, x2, y2 = box
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                active_centroids[track_id] = (cx, cy)

                if track_id not in tracking_memory:
                    tracking_memory[track_id] = deque(maxlen=SEQUENCE_LENGTH)
                tracking_memory[track_id].append((cx, cy))

                # --- VISUAL DEBUG 1: THE BLUE DOTS ---
                cv2.circle(last_annotated_frame, (cx, cy), 6, (255, 255, 0), -1)

                # --- VISUAL DEBUG 2: THE YELLOW MEMORY TRAILS ---
                history = list(tracking_memory[track_id])
                for i in range(1, len(history)):
                    cv2.line(last_annotated_frame, history[i - 1], history[i], (0, 255, 255), 2)

            for id1, id2 in itertools.combinations(active_centroids.keys(), 2):
                pt1 = active_centroids[id1]
                pt2 = active_centroids[id2]
                distance = math.sqrt((pt2[0] - pt1[0])**2 + (pt2[1] - pt1[1])**2)
                
                # --- NEW: RAW MATH DIAGNOSTIC ---
                print(f"Distance between ID {id1} & {id2}: {int(distance)}px")

                if distance < MIN_SAFE_DISTANCE:
                    # --- VISUAL DEBUG 3: THE RED PROXIMITY LINE ---
                    cv2.line(last_annotated_frame, pt1, pt2, (0, 0, 255), 3)
                    
                    if len(tracking_memory[id1]) == SEQUENCE_LENGTH and len(tracking_memory[id2]) == SEQUENCE_LENGTH:
                        hist1 = list(tracking_memory[id1])
                        hist2 = list(tracking_memory[id2])
                        sequence_matrix = []
                        prev_dist = None
                        
                        for i in range(SEQUENCE_LENGTH):
                            p1_hist = hist1[i]
                            p2_hist = hist2[i]
                            historical_dist = math.sqrt((p2_hist[0] - p1_hist[0])**2 + (p2_hist[1] - p1_hist[1])**2)
                            delta_dist = 0 if prev_dist is None else historical_dist - prev_dist
                            prev_dist = historical_dist
                            sequence_matrix.append([historical_dist, delta_dist])
                        
                        tensor_input = np.array([sequence_matrix], dtype=np.float32)
                        prediction = temporal_brain.predict(tensor_input, verbose=0)[0][0]
                        
                        if prediction > 0.50:
                            cv2.putText(last_annotated_frame, f"VIOLENCE ALERT: {prediction*100:.0f}%", 
                                        (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 4)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time

    display_frame = last_annotated_frame.copy()
    cv2.putText(display_frame, f"System FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Smart Campus - Phase 1 Active", display_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()