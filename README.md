# Smart Surveillance: AI-Powered Fall Detection & Alert System

This project uses YOLOv8-pose for real-time human pose detection to identify falls and triggers an emergency SMS alert via Twilio.

## Features
- **Real-time Fall Detection:** Uses YOLOv8 pose estimation to detect falls based on bounding box aspect ratio and temporal consistency.
- **Automated Alerts:** Integrates with Twilio API to send SMS notifications to security personnel.
- **Spam Prevention:** Includes cooldown logic to avoid sending multiple alerts for the same event.
- **Visual Feedback:** Annotates the live camera feed with detection results and warning messages.

## Project Structure
- `yolo_tracker.py`: Main entry point for camera capture, object detection, and fall logic.
- `alert_router.py`: Handles communication with the Twilio API.
- `yolov8n-pose.pt`: Pre-trained YOLOv8 pose model.
- `.gitignore`: Configured to ignore virtual environments and sensitive files.

## Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd smart_surveillance
   ```

2. **Install dependencies:**
   ```bash
   pip install opencv-python ultralytics twilio
   ```

3. **Configure Twilio:**
   Update `alert_router.py` with your Twilio credentials:
   ```python
   TWILIO_ACCOUNT_SID = 'YOUR_ACCOUNT_SID_HERE'
   TWILIO_AUTH_TOKEN = 'YOUR_AUTH_TOKEN_HERE'
   TWILIO_VIRTUAL_NUMBER = '+1234567890'
   SECURITY_GUARD_NUMBER = '+919876543210'
   ```

4. **Run the application:**
   ```bash
   python yolo_tracker.py
   ```

## Requirements
- Python 3.8+
- Webcam or video source
- Twilio account (for SMS alerts)

## Disclaimer
This is a prototype for educational purposes. Ensure proper API security and testing before using in a production environment.
