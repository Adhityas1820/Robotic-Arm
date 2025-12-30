import json
import serial
import time
import cv2
import numpy as np
import base64
import math
from google import genai

import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

current_angle = 90

# Color ranges for tracking
pink_lower = np.array([0, 80, 150])
pink_upper = np.array([10, 180, 255])
green_lower = np.array([25, 140, 200])
green_upper = np.array([45, 180, 240])

# Keep camera open for tracking
cap = cv2.VideoCapture(1)

def send_command(cmd):
    arduino.write((cmd + '\n').encode())
    print("Sent:", cmd)

def update_angle(angle):
    global current_angle
    angle = max(0, min(180, int(angle)))
    current_angle = angle
    arduino.write((f"SERVO_ANGLE_{angle}\n").encode())

def get_angle(from_point, to_point):
    """Get angle in degrees from one point to another."""
    dx = to_point[0] - from_point[0]
    dy = to_point[1] - from_point[1]
    return math.degrees(math.atan2(dy, dx))

def detect_markers(frame):
    """Detect tip and axis markers in frame."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    tip_pos = None
    axis_pos = None
    
    # Detect pink (tip)
    pink_mask = cv2.inRange(hsv, pink_lower, pink_upper)
    pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if pink_contours:
        largest = max(pink_contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 50:
            x, y, w, h = cv2.boundingRect(largest)
            tip_pos = (x + w//2, y + h//2)
    
    # Detect green (axis)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if green_contours:
        largest = max(green_contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 50:
            x, y, w, h = cv2.boundingRect(largest)
            axis_pos = (x + w//2, y + h//2)
    
    return tip_pos, axis_pos

def visual_point(target_x, target_y, target_name="object"):
    """Align servo to point at target using visual feedback."""
    global current_angle
    
    target_pos = (target_x, target_y)
    print(f"Aligning to '{target_name}' at {target_pos}...")
    
    cv2.namedWindow("Alignment")
    
    for i in range(50):
        ret, frame = cap.read()
        if not ret:
            print("Camera error")
            return False
        
        tip_pos, axis_pos = detect_markers(frame)
        
        # Draw target
        cv2.circle(frame, target_pos, 15, (0, 0, 255), 2)
        cv2.putText(frame, target_name, (target_pos[0]+15, target_pos[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        if not tip_pos or not axis_pos:
            print("Lost markers, retrying...")
            cv2.putText(frame, "LOST MARKERS", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            cv2.imshow("Alignment", frame)
            cv2.waitKey(1)
            time.sleep(0.1)
            continue
        
        # Draw markers
        cv2.circle(frame, tip_pos, 10, (255, 0, 255), 2)
        cv2.putText(frame, "TIP", (tip_pos[0]+15, tip_pos[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        
        cv2.circle(frame, axis_pos, 10, (0, 255, 0), 2)
        cv2.putText(frame, "AXIS", (axis_pos[0]+15, axis_pos[1]), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Draw line from axis to tip (yellow)
        cv2.line(frame, axis_pos, tip_pos, (0, 255, 255), 2)
        
        # Extend line to show where servo is pointing
        dx = tip_pos[0] - axis_pos[0]
        dy = tip_pos[1] - axis_pos[1]
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            extend = 300
            end_x = int(tip_pos[0] + (dx/length) * extend)
            end_y = int(tip_pos[1] + (dy/length) * extend)
            cv2.line(frame, tip_pos, (end_x, end_y), (0, 255, 255), 1)
        
        # Draw line from axis to target (red)
        cv2.line(frame, axis_pos, target_pos, (0, 0, 255), 2)
        
        # Calculate error
        angle_to_tip = get_angle(axis_pos, tip_pos)
        angle_to_target = get_angle(axis_pos, target_pos)
        error = angle_to_target - angle_to_tip
        
        # Show info on frame
        cv2.putText(frame, f"Servo: {current_angle} deg", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Error: {error:.1f} deg", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Step: {i+1}/50", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Alignment", frame)
        cv2.waitKey(1)
        
        print(f"  Step {i+1}: Error = {error:.1f}° | Servo at {current_angle}°")
        
        # Check if aligned
        if abs(error) < 2:
            print(f"Aligned to '{target_name}'!")
            cv2.putText(frame, "ALIGNED!", (10, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Alignment", frame)
            cv2.waitKey(1000)  # Show success for 1 second
            cv2.destroyWindow("Alignment")
            return True
        
        # Adjust servo
        adjustment = error * 0.5
        new_angle = current_angle + adjustment
        update_angle(new_angle)
        
        time.sleep(0.15)
    
    print("Could not align within 50 steps")
    cv2.destroyWindow("Alignment")
    return False
            
def capture_image():
    ret, frame = cap.read()
    return frame if ret else None

def image_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def show_image(frame):
    cv2.imshow("Captured Image - Press any key", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def ask_gemini(prompt):
    frame = capture_image()
    if frame is None:
        print("Error: Could not capture image")
        return "[]"
    
    height, width = frame.shape[:2]
    
    print("Showing captured image...")
    show_image(frame)
    
    system_message = (
        "You are an assistant that controls an Arduino with LEDs and a servo motor.\n\n"
        
        "Available commands:\n"
        "- LED1_ON, LED1_OFF\n"
        "- LED2_ON, LED2_OFF\n"
        "- LED3_ON, LED3_OFF\n"
        "- SERVO_ANGLE_X (where X is 0-180, for blind movement)\n"
        "- VISUAL_POINT (to point at something you can see in the image)\n\n"
        
        f"Current servo position: {current_angle} degrees\n"
        f"Image dimensions: {width}px wide, {height}px tall\n\n"
        
        "An image from the camera is provided. Use it if the request requires vision.\n\n"
        
        "Respond with ONLY a JSON array of commands. Each command has:\n"
        "- \"cmd\": the command string\n"
        "- \"delay\": milliseconds to wait after\n\n"
        
        "For VISUAL_POINT, also include:\n"
        "- \"target\": what you're pointing at\n"
        "- \"x\": the x pixel coordinate (0 = left, " + str(width) + " = right)\n"
        "- \"y\": the y pixel coordinate (0 = top, " + str(height) + " = bottom)\n\n"
        
        "Example for blind movement:\n"
        "[{\"cmd\": \"SERVO_ANGLE_90\", \"delay\": 500}]\n\n"
        
        "Example for pointing at something:\n"
        "[{\"cmd\": \"VISUAL_POINT\", \"target\": \"water bottle\", \"x\": 320, \"y\": 240, \"delay\": 500}]\n\n"
        
        "If the request doesn't apply (e.g., object not visible), respond with: []\n\n"
        
        f"User request: {prompt}"
    )
    
    image_b64 = image_to_base64(frame)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "parts": [
                    {"text": system_message},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_b64
                        }
                    }
                ]
            }
        ]
    )
    
    return response.text

def execute_commands(commands):
    for step in commands:
        cmd = step["cmd"]
        
        if cmd == "VISUAL_POINT":
            x = step["x"]
            y = step["y"]
            target = step.get("target", "object")
            visual_point(x, y, target)
        elif cmd.startswith("SERVO_ANGLE_"):
            send_command(cmd)
            angle = int(cmd.replace("SERVO_ANGLE_", ""))
            update_angle(angle)
        else:
            send_command(cmd)
        
        time.sleep(step["delay"] / 1000)

# Main loop
print("=== Gemini Servo Controller ===")
print("Commands: 'point at the [object]', 'turn on LED1', etc.")
print("Type 'quit' to exit\n")

while True:
    user_input = input("Ask Gemini: ")
    if user_input.strip().lower() == "quit":
        break
    if user_input.strip() == "":
        continue

    response = ask_gemini(user_input)
    print("Gemini response:")
    print(response)

    # Strip markdown code blocks if present
    clean_response = response.strip()
    if clean_response.startswith("```"):
        clean_response = clean_response.split("\n", 1)[1]
        clean_response = clean_response.rsplit("```", 1)[0]

    try:
        commands = json.loads(clean_response)
        if commands:
            print("Executing commands...")
            execute_commands(commands)
            print(f"Done. Servo now at {current_angle} degrees.")
        else:
            print("No commands to execute.")
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)

# Cleanup
cap.release()
cv2.destroyAllWindows()
arduino.close()
print("Goodbye!")