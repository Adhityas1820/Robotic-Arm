import cv2
import serial
import time
import json

# Connect to Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

# Starting position
current_angle = 90

# Calibration values (to be set)
left_angle = None
right_angle = None

def send_angle(angle):
    global current_angle
    angle = max(0, min(180, angle))  # Constrain to 0-180
    current_angle = angle
    arduino.write((f"SERVO_ANGLE_{angle}\n").encode())
    print(f"Servo: {angle}°")

# Send initial position
send_angle(current_angle)

# Open camera
cap = cv2.VideoCapture(1)

print("\n=== Calibration Tool ===")
print("Arrow Left/Right: Move servo by 10°")
print("A/D: Move servo by 1° (fine tune)")
print("L: Save LEFT edge angle")
print("R: Save RIGHT edge angle")
print("S: Save calibration to file")
print("Q: Quit")
print("========================\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Draw crosshair in center
    h, w = frame.shape[:2]
    cv2.line(frame, (w//2, 0), (w//2, h), (0, 255, 0), 1)
    cv2.line(frame, (0, h//2), (w, h//2), (0, 255, 0), 1)
    
    # Draw info on frame
    info = f"Servo: {current_angle} deg"
    cv2.putText(frame, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    left_text = f"Left edge: {left_angle}" if left_angle else "Left edge: NOT SET (press L)"
    right_text = f"Right edge: {right_angle}" if right_angle else "Right edge: NOT SET (press R)"
    cv2.putText(frame, left_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    cv2.putText(frame, right_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    cv2.imshow("Calibration - Point servo at screen edges", frame)
    
    key = cv2.waitKey(1) & 0xFF
    
    # Movement controls
    if key == 81 or key == 2:  # Left arrow
        send_angle(current_angle + 10)
    elif key == 83 or key == 3:  # Right arrow
        send_angle(current_angle - 10)
    elif key == ord('a'):  # Fine tune left
        send_angle(current_angle + 1)
    elif key == ord('d'):  # Fine tune right
        send_angle(current_angle - 1)
    
    # Save calibration points
    elif key == ord('l'):
        left_angle = current_angle
        print(f"LEFT edge saved: {left_angle}°")
    elif key == ord('r'):
        right_angle = current_angle
        print(f"RIGHT edge saved: {right_angle}°")
    
    # Save to file
    elif key == ord('s'):
        if left_angle is not None and right_angle is not None:
            calibration = {
                "left_angle": left_angle,
                "right_angle": right_angle,
                "frame_width": w
            }
            with open("calibration.json", "w") as f:
                json.dump(calibration, f, indent=2)
            print(f"\nCalibration saved to calibration.json:")
            print(f"  Left edge:  {left_angle}°")
            print(f"  Right edge: {right_angle}°")
            print(f"  Frame width: {w}px\n")
        else:
            print("Set both LEFT and RIGHT angles first!")
    
    # Quit
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
print("Calibration tool closed.")