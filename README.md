# Robotic-Arm
# 🤖 AI Robotic Arm

An AI-powered robotic arm that understands natural language and sees the world. Tell it what to do, and it figures out the rest.

> "Point at the scissors" → Gemini sees the scissors → Servo points at them

---

## 🎥 Demo

*Coming soon*

---

## 🎯 What It Does

You speak naturally. The robot understands.

| You Say | What Happens |
|---------|--------------|
| "Point at the water bottle" | Gemini locates it, servo points at it |
| "Turn on LED 1" | LED turns on |
| "Sweep left to right" | Servo scans the area |
| "Point at the red object" | Finds and points at red objects |

---

## 🧠 How It Works
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   You       │────▶│   Gemini    │────▶│  Arduino    │
│  (command)  │     │  (vision +  │     │  (servo +   │
│             │     │   brain)    │     │   LEDs)     │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   OpenCV    │
                    │  (visual    │
                    │  feedback)  │
                    └─────────────┘
```

### The Visual Feedback Loop

This is the cool part. Instead of calculating exact angles mathematically, the system **watches itself** and self-corrects:

1. Gemini identifies target coordinates from the image
2. OpenCV tracks colored markers on the servo arm
3. System calculates error between "where it's pointing" and "where it should point"
4. Servo adjusts until aligned
5. Repeat until error < 2°

**This makes it accurate without precise calibration.**

---

## 🛠️ Tech Stack

| Component | Purpose |
|-----------|---------|
| **Google Gemini API** | Vision + natural language understanding |
| **OpenCV** | Real-time marker tracking |
| **Python** | Core application |
| **Arduino** | Hardware control |
| **Servo Motor** | Physical pointing |

---

## 📦 Hardware Setup
```
Camera (iPad via Camo)
       │
       ▼
 ┌───────────┐
 │  Scene    │ ← Objects to point at
 └───────────┘
       │
       ▼
    [Servo]
       │
       ▼
   Arduino
```

### Components
- Arduino Uno
- Servo motor (with colored markers for tracking)
- 3x LEDs
- Webcam or phone camera (I used iPad + Camo)

### Marker Setup
- **Green marker** on servo axis (pivot point)
- **Pink marker** on servo arm tip

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/robotic-arm.git
cd robotic-arm
```

### 2. Install dependencies
```bash
pip install opencv-python numpy pyserial google-genai
```

### 3. Set up your API key
```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Upload Arduino code
Upload `arduino/servo_control.ino` to your Arduino.

### 5. Run it
```bash
python main.py
```

---

## 📁 Project Structure
```
robotic-arm/
├── main.py              # Main application
├── calibration.py       # Calibration tool
├── test_tracking.py     # Test marker detection
├── arduino/
│   └── servo_control.ino
├── calibration.json     # Saved calibration data
└── README.md
```

---

## 🎮 Commands

### Visual Commands (uses camera)
- `"Point at the [object]"`
- `"Find the [object]"`
- `"Where is the [object]?"`

### Blind Commands (no camera needed)
- `"Look left"` / `"Look right"`
- `"Go to 90 degrees"`
- `"Sweep back and forth"`

### LED Commands
- `"Turn on LED 1"`
- `"Turn off all LEDs"`
- `"Blink LED 2"`

---

## 📍 Current Status

- ✅ Natural language control via Gemini
- ✅ Visual object detection
- ✅ Self-correcting visual feedback loop
- ✅ Real-time marker tracking
- ✅ LED control
- 🔄 **In Progress:** Multi-joint arm
- 🔄 **In Progress:** Gripper for picking up objects


---

## 🔮 Future Plans

1. **Add gripper** — Pick up and move objects
2. **More joints** — Full arm with shoulder, elbow, wrist
3. **Object tracking** — Follow moving objects
4. **Voice control** — Speak commands instead of typing

---

## 📝 What I Learned

- Integrating LLMs with physical hardware
- Visual feedback loops for self-correcting systems
- HSV color space for reliable object tracking
- Serial communication between Python and Arduino
- Building end-to-end AI systems

---

## 🤝 Contributing

This is a personal project, but feel free to fork it and build your own version!

---

## 📄 License

MIT License — do whatever you want with it.

---

### Built by Adhitya 

*Started as a late-night coding session. Ended up becoming a robot.*
