import cv2
import numpy as np

cap = cv2.VideoCapture(1)

# Color ranges in HSV
# Salmon pink (ff837c)
# Color ranges
# Pink (tip)
pink_lower = np.array([0, 80, 150])
pink_upper = np.array([10, 180, 255])

# Yellow-green (axis) - your actual values
green_lower = np.array([25, 140, 200])
green_upper = np.array([45, 180, 240])
print("Tracking salmon pink (tip) and yellow-green (axis)")
print("Press Q to quit")

mouse_x, mouse_y = 0, 0

def mouse_callback(event, x, y, flags, param):
    global mouse_x, mouse_y
    mouse_x, mouse_y = x, y

cv2.namedWindow("Tracking")
cv2.setMouseCallback("Tracking", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Get HSV value at mouse position (for tuning)
    hsv_at_mouse = hsv[mouse_y, mouse_x]
    
    # Detect pink (tip)
    pink_mask = cv2.inRange(hsv, pink_lower, pink_upper)
    
    # Detect green (axis)
    green_mask = cv2.inRange(hsv, green_lower, green_upper)
    
    # Find pink contours (tip)
    pink_contours, _ = cv2.findContours(pink_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    tip_pos = None
    if pink_contours:
        largest = max(pink_contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area > 50:
            x, y, w, h = cv2.boundingRect(largest)
            tip_pos = (x + w//2, y + h//2)
            cv2.circle(frame, tip_pos, 10, (255, 0, 255), 2)
            cv2.putText(frame, f"TIP {tip_pos}", (tip_pos[0]+15, tip_pos[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
    
    # Find green contours (axis)
    green_contours, _ = cv2.findContours(green_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    axis_pos = None
    if green_contours:
        largest = max(green_contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area > 50:
            x, y, w, h = cv2.boundingRect(largest)
            axis_pos = (x + w//2, y + h//2)
            cv2.circle(frame, axis_pos, 10, (0, 255, 0), 2)
            cv2.putText(frame, f"AXIS {axis_pos}", (axis_pos[0]+15, axis_pos[1]), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw line between axis and tip if both detected
    if tip_pos and axis_pos:
        cv2.line(frame, axis_pos, tip_pos, (255, 255, 0), 2)
    
    # Show HSV at mouse position (for tuning)
    cv2.putText(frame, f"HSV at cursor: {hsv_at_mouse}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("Tracking", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()