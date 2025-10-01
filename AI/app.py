from flask import Flask, render_template, Response, jsonify
import requests
import numpy as np
import cv2
from ultralytics import YOLO

app = Flask(__name__)
current_count = 0

ESP32_IP = "192.168.17.48"
VIDEO_URL = f"http://{ESP32_IP}/capture"  # Using snapshot loop

# Load YOLO model
model = YOLO("yolov8n.pt")

# -----------------------
# Video generator with detection
# -----------------------
def gen_frames():
    global current_count
    while True:
        try:
            # Get single snapshot
            resp = requests.get(VIDEO_URL, timeout=5)
            img_array = np.frombuffer(resp.content, np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is None:
                continue

            # YOLO detection
            results = model(frame)[0]
            people_count = 0
            for box in results.boxes:
                cls_id = int(box.cls[0])
                if model.names[cls_id] == "person":
                    people_count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

            current_count = people_count

            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print("Error reading frame:", e)
            continue

# -----------------------
# Count API with density
# -----------------------
@app.route("/count")
def count():
    global current_count
    density = "Low"
    if current_count == 1:
        density = "Low"
    elif 1 < current_count <= 5:
        density = "Medium"
    elif current_count > 5:
        density = "High"
    
    return jsonify({
        "current_count": current_count,
        "density": density
    })

# -----------------------
# Routes
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# -----------------------
# Run app
# -----------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
