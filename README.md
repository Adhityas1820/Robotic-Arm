# AI Robotic Arm

A robotic arm controlled by natural language using Google Gemini and computer vision.

## What It Does

Speak naturally, and the robot understands:

- "Point at the scissors" → Gemini locates it, servo points at it
- "Turn on LED 1" → LED turns on
- "Sweep left to right" → Servo scans the area

## How It Works

1. You give a command
2. Gemini analyzes the camera feed and decides what to do
3. OpenCV tracks markers on the servo arm
4. Visual feedback loop adjusts until aligned

The system watches itself and self-corrects rather than relying on precise calibration.
## Video demo

Coming soon

## Tech Stack

- Google Gemini API (vision + language)
- OpenCV (marker tracking)
- Python
- Arduino + Servo

## Current Status

Done:
- Natural language control
- Visual feedback loop
- Real-time marker tracking

In progress:
- Multi-joint arm
- Gripper for picking up objects

## Setup

1. Clone the repo
2. Install dependencies: `pip install opencv-python numpy pyserial google-genai`
3. Set your API key: `export GEMINI_API_KEY="your-key"`
4. Upload Arduino code
5. Run: `python main.py`

