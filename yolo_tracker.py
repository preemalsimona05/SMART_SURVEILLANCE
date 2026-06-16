import cv2
from ultralytics import YOLO
import time

# --- NEW: Import your communication microservice ---
import alert_router

print("Loading YOLOv8 Pose Engine...")
model = YOLO('yolov8n-pose.pt')

cap = cv2.VideoCapture(0)
prev_time = 0

ASPECT_RATIO_THRESHOLD = 1.2   
REQUIRED_CONSECUTIVE_FRAMES = 10  

fall_frame_counter = 0

print("\nAI + SMS Alert System Active. Simulating a fall will trigger the network protocol.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    results = model.predict(source=frame, save=False, verbose=False)
    annotated_frame = results[0].plot()

    if len(results[0].boxes) > 0:
        box = results[0].boxes[0].xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
        
        box_width = x2 - x1
        box_height = y2 - y1
        
        if box_height > 0:
            aspect_ratio = box_width / box_height
            
            if aspect_ratio > ASPECT_RATIO_THRESHOLD:
                fall_frame_counter += 1
            else:
                fall_frame_counter = 0

            # --- THE CRITICAL TRIGGER GATE ---
            if fall_frame_counter >= REQUIRED_CONSECUTIVE_FRAMES:
                # 1. Draw the visual warning on the camera feed
                cv2.rectangle(annotated_frame, (0, 0), (frame.shape[1], 80), (0, 0, 255), -1)
                cv2.putText(annotated_frame, "CRITICAL: FALL CONFIRMED", (50, 55), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3)
                
                # 2. Fire the SMS alert via the router file
                alert_router.trigger_sms_alert("Campus_Gate_Camera_01", "Severe Fall / Physical Anomaly")
                
                # Reset the counter so it doesn't get stuck in a loop
                fall_frame_counter = 0
    else:
        fall_frame_counter = 0

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time) if (curr_time - prev_time) > 0 else 0
    prev_time = curr_time
    
    cv2.putText(annotated_frame, f"FPS: {int(fps)} | Fall Counter: {fall_frame_counter}", 
                (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow("Smart Campus - Upgraded Fall Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()