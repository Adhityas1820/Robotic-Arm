import serial
import time

# Connect to Arduino
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Wait for Arduino to reset

def send_command(cmd, delay_after=0.5):
    """Send a command to Arduino and wait."""
    arduino.write((cmd + '\n').encode())
    print(f"Sent: {cmd}")
    time.sleep(delay_after)

def test_leds():
    """Test all LEDs on and off."""
    print("\n=== Testing LEDs ===")
    
    # Turn each LED on one by one
    for i in range(1, 4):
        send_command(f"LED{i}_ON")
    
    time.sleep(1)
    
    # Turn each LED off one by one
    for i in range(1, 4):
        send_command(f"LED{i}_OFF")

def test_led_blink():
    """Blink all LEDs together."""
    print("\n=== Testing LED Blink ===")
    
    for _ in range(3):
        # All on
        for i in range(1, 4):
            send_command(f"LED{i}_ON", delay_after=0.1)
        time.sleep(0.3)
        
        # All off
        for i in range(1, 4):
            send_command(f"LED{i}_OFF", delay_after=0.1)
        time.sleep(0.3)

def test_servo_presets():
    """Test servo preset positions."""
    print("\n=== Testing Servo Presets ===")
    
    positions = [0, 45, 90, 135, 180, 90, 0]
    for pos in positions:
        send_command(f"SERVO_{pos}", delay_after=0.7)

def test_servo_sweep():
    """Sweep servo from 0 to 180 and back."""
    print("\n=== Testing Servo Sweep ===")
    
    # Sweep up
    for angle in range(0, 181, 10):
        send_command(f"SERVO_ANGLE_{angle}", delay_after=0.1)
    
    # Sweep down
    for angle in range(180, -1, -10):
        send_command(f"SERVO_ANGLE_{angle}", delay_after=0.1)

def test_combined():
    """Test LEDs and servo together."""
    print("\n=== Testing Combined ===")
    
    send_command("SERVO_0", delay_after=0.5)
    
    # LED chase with servo following
    for i in range(1, 4):
        send_command(f"LED{i}_ON", delay_after=0.1)
        send_command(f"SERVO_ANGLE_{i * 60}", delay_after=0.4)
        send_command(f"LED{i}_OFF", delay_after=0.1)
    
    # Return servo to center
    send_command("SERVO_90", delay_after=0.5)

def main():
    print("Starting Arduino Component Tests")
    print("=" * 40)
    
    try:
        test_leds()
        test_led_blink()
        test_servo_presets()
        test_servo_sweep()
        test_combined()
        
        print("\n" + "=" * 40)
        print("All tests complete!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    finally:
        # Turn everything off
        print("\nCleaning up...")
        for i in range(1, 4):
            send_command(f"LED{i}_OFF", delay_after=0.1)
        send_command("SERVO_0", delay_after=0.5)
        arduino.close()
        print("Done.")

if __name__ == "__main__":
    main()