# OpenCV Face Switch

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5%2B-green)](https://opencv.org/)
[![Arduino](https://img.shields.io/badge/Arduino-Uno%2FNano-orange)](https://www.arduino.cc/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 📋 Overview

**OpenCV Face Switch** is an innovative hands-free lighting control system that uses computer vision to detect human faces in real-time and control an LED through an Arduino microcontroller. When a face is detected by the webcam, the LED automatically turns ON; when no face is present, the LED turns OFF.

### ✨ Features
- Real-time face detection using OpenCV
- Automatic LED control based on face presence
- Live video feed with face tracking display
- Smooth operation with cooldown mechanism
- Cross-platform compatibility
- User-friendly interface with status display

### 🎯 Applications
- Smart lighting systems
- Security and surveillance
- Interactive art installations
- Accessibility solutions
- Educational tool for IoT and computer vision

## 📦 Hardware Requirements
| Component | Specification | Quantity |
|-----------|--------------|----------|
| Arduino Board | Uno/Nano/Mega | 1 |
| LED | 5mm (any color) | 1 |
| Resistor | 220Ω | 1 |
| Webcam | USB (720p/1080p) | 1 |
| Breadboard | 400 points | 1 |
| Jumper Wires | M/M, M/F | 10 |
| USB Cable | A to B | 1 |

## 💻 Software Requirements
- Python 3.7+
- OpenCV 4.5+
- PySerial 3.4+
- NumPy 1.19+
- Arduino IDE

## 🔧 Complete Setup Guide

### Step 1: Hardware Wiring

Arduino Pin 7 -----> [220Ω Resistor] -----> LED(+) -----> LED(-) -----> GND


### Step 2: Install Python Dependencies

pip install opencv-python pyserial numpy

Step 3: Arduino Code
Copy and upload this code to your Arduino:

/*
 * OpenCV Face Switch - Arduino Firmware
 * Commands: 'H' - LED ON, 'L' - LED OFF
 */

const int LED_PIN = 7;
const int BAUD_RATE = 9600;
char command;

void setup() {
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(BAUD_RATE);
    digitalWrite(LED_PIN, LOW);
    Serial.println("Arduino Ready");
}

void loop() {
    if (Serial.available() > 0) {
        command = Serial.read();
        if (command == 'H' || command == 'h') {
            digitalWrite(LED_PIN, HIGH);
            Serial.println("LED ON");
        }
        else if (command == 'L' || command == 'l') {
            digitalWrite(LED_PIN, LOW);
            Serial.println("LED OFF");
        }
    }
    delay(10);
}

Step 4: Python Code
Save this as face_switch.py:

#!/usr/bin/env python3
"""
OpenCV Face Switch - Main Program
Controls Arduino LED based on face detection
"""

import cv2
import serial
import time
import numpy as np

# ========== CONFIGURATION ==========
ARDUINO_PORT = 'COM6'  # Change this! (Windows: COM3, COM4; Linux/Mac: /dev/ttyUSB0)
BAUD_RATE = 9600
COOLDOWN = 0.5  # Seconds between commands
# ====================================

class FaceSwitch:
    def __init__(self):
        self.arduino = None
        self.cap = None
        self.face_cascade = None
        self.face_detected = False
        self.last_command = 0
        
    def connect_arduino(self):
        """Connect to Arduino"""
        try:
            self.arduino = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)
            print(f"✅ Connected to Arduino on {ARDUINO_PORT}")
            return True
        except Exception as e:
            print(f"❌ Arduino connection failed: {e}")
            print("Tips: Check port number, close Arduino IDE, check USB")
            return False
    
    def init_camera(self):
        """Initialize webcam"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ Camera failed to open")
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("✅ Camera initialized")
        return True
    
    def init_face_detector(self):
        """Load face detection model"""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            print("❌ Face detector failed to load")
            return False
        print("✅ Face detector loaded")
        return True
    
    def send_command(self, cmd):
        """Send command to Arduino with cooldown"""
        now = time.time()
        if now - self.last_command > COOLDOWN:
            self.arduino.write(cmd.encode())
            self.last_command = now
            print(f"📤 Command: {cmd} - LED {'ON' if cmd=='H' else 'OFF'}")
    
    def run(self):
        """Main program loop"""
        print("\n" + "="*50)
        print("🚀 OPENCV FACE SWITCH STARTING")
        print("="*50)
        
        # Initialize all components
        if not all([self.connect_arduino(), self.init_camera(), self.init_face_detector()]):
            print("❌ Initialization failed!")
            return
        
        print("\n✅ SYSTEM READY!")
        print("👤 Show face → LED ON")
        print("👤 Hide face → LED OFF")
        print("❌ Press 'q' to quit\n")
        
        self.send_command('L')  # Start with LED off
        
        try:
            while True:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # Mirror and convert to grayscale
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(
                    gray, 1.1, 5, minSize=(100, 100)
                )
                
                # Draw rectangles around faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, "FACE", (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Control LED based on face detection
                current_faces = len(faces) > 0
                if current_faces != self.face_detected:
                    cmd = 'H' if current_faces else 'L'
                    self.send_command(cmd)
                    self.face_detected = current_faces
                
                # Display status
                status = f"FACE: {'DETECTED' if current_faces else 'NOT DETECTED'}"
                color = (0, 255, 0) if current_faces else (0, 0, 255)
                
                # Add background for text
                cv2.rectangle(frame, (5, 5), (300, 35), (0, 0, 0), -1)
                cv2.putText(frame, status, (10, 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                cv2.putText(frame, f"LED: {'ON' if self.face_detected else 'OFF'}", 
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.putText(frame, "Press 'q' to quit", (frame.shape[1]-150, 25),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
                
                # Show frame
                cv2.imshow('OpenCV Face Switch', frame)
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n👋 Quitting...")
                    break
                    
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            # Cleanup
            if self.arduino:
                self.send_command('L')
                self.arduino.close()
            if self.cap:
                self.cap.release()
            cv2.destroyAllWindows()
            print("✅ Cleanup complete")

# ========== MAIN ==========
if __name__ == "__main__":
    app = FaceSwitch()
    app.run()

Step 5: Requirements File
Save this as requirements.txt:

opencv-python>=4.5.0
pyserial>=3.4
numpy>=1.19.0

🚀 Quick Start Guide
Wire the circuit as shown above

Upload Arduino code to your board

Update the port in Python code (line 14): Change COM6 to your port

Windows: COM3, COM4, etc.

Linux: /dev/ttyUSB0, /dev/ttyACM0

Mac: /dev/cu.usbmodem*

Install dependencies: pip install -r requirements.txt

Run the program: python face_switch.py

Show your face to the camera to turn LED ON

Press 'q' to quit

📊 Troubleshooting
Problem	Solution
Arduino not connecting	Check port number, close Arduino IDE, restart program
Camera not working	Check connections, try camera_id=1 in code
No face detection	Adjust lighting, face camera directly, check distance
LED not turning on	Check wiring, resistor value, Arduino pin
Slow performance	Reduce camera resolution, close other programs

opencv-face-switch/
│
├── face_switch.py          # Main Python program
├── face_switch.ino         # Arduino code
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── LICENSE                 # MIT License


🔄 How It Works
Webcam captures video frames in real-time

OpenCV detects faces using Haar Cascade classifier

Python sends 'H' (ON) or 'L' (OFF) via serial port

Arduino receives command and controls LED

Display shows detection status and visual feedback

 Learning Outcomes
Computer vision fundamentals with OpenCV

Serial communication between Python and Arduino

Hardware-software integration

Real-time image processing

Event-driven programming

IoT concepts and implementation

🚀 Future Enhancements
Multiple face detection and counting

Face recognition for personalized control

Web interface for remote monitoring

Mobile app control

Cloud data logging

Gesture recognition

Multiple LED control

Brightness control based on face distance


👤 Author
Abdirahim Bashir


