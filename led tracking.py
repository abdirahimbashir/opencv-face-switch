import cv2
import serial
import time
import numpy as np

# Arduino serial connection - Updated to COM6
arduino_port = 'COM6'  # Changed to your COM6 port
baud_rate = 9600

# Initialize serial connection
try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(2)  # Wait for connection to establish
    print(f"✅ Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"❌ Failed to connect to Arduino on {arduino_port}")
    print(f"Error: {e}")
    print("Please check:")
    print("1. Arduino is connected")
    print("2. No other program is using COM6")
    print("3. The correct port number")
    exit()

# Initialize face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Check if face cascade loaded properly
if face_cascade.empty():
    print("❌ Failed to load face cascade classifier")
    exit()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Failed to open webcam")
    exit()
    
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n🎥 Face-Controlled LED Started!")
print("📡 Controlling LED on Arduino (COM6)")
print("👤 Show your face to turn LED ON")
print("👤 Hide your face to turn LED OFF")
print("Press 'q' to quit\n")

# Variables for smoothing
face_detected = False
last_command_time = 0
cooldown_period = 0.5  # Minimum time between commands (seconds)
frame_count = 0

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    frame_count += 1
    # Mirror the frame horizontally for more intuitive interaction
    frame = cv2.flip(frame, 1)
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces (process every other frame to improve performance)
    if frame_count % 2 == 0:
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        
        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, "Face Detected", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Determine if face is detected
        current_face_detected = len(faces) > 0
        
        # Send command to Arduino (with cooldown)
        current_time = time.time()
        if current_face_detected != face_detected and current_time - last_command_time > cooldown_period:
            if current_face_detected:
                arduino.write(b'H')  # Send 'H' to turn LED ON
                print(f"🟢 {time.strftime('%H:%M:%S')} - Face detected - LED ON")
            else:
                arduino.write(b'L')  # Send 'L' to turn LED OFF
                print(f"🔴 {time.strftime('%H:%M:%S')} - No face detected - LED OFF")
            
            face_detected = current_face_detected
            last_command_time = current_time
    
    # Display status on frame
    status = "FACE DETECTED: YES" if face_detected else "FACE DETECTED: NO"
    color = (0, 255, 0) if face_detected else (0, 0, 255)
    
    # Add background for better readability
    cv2.rectangle(frame, (5, 5), (300, 70), (0, 0, 0), -1)
    cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                0.8, color, 2)
    cv2.putText(frame, f"LED: {'ON' if face_detected else 'OFF'}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Add instructions
    cv2.putText(frame, "Press 'q' to quit", (frame.shape[1] - 150, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Show frame
    cv2.imshow('Face Controlled LED - COM6', frame)
    
    # Break loop on 'q' press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n👋 Quitting...")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
if arduino.is_open:
    arduino.write(b'L')  # Turn LED off before closing
    time.sleep(0.1)
    arduino.close()
print("✅ Program ended - LED turned off")