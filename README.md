# Autonomous Obstacle Avoiding Robot using Raspberry Pi & VL53L5CX

An intelligent autonomous obstacle avoiding robot powered by the **Raspberry Pi 5** and the **VL53L5CX 8x8 Time-of-Flight sensor**.

Unlike traditional ultrasonic-based robots, this project uses real-time spatial depth sensing to make smarter and faster navigation decisions.

The robot continuously scans its surroundings, detects nearby obstacles, determines the safest free path, and autonomously navigates around objects using differential steering.

---

# Project Overview

This project demonstrates how a low-cost Time-of-Flight sensor can be used to build a responsive autonomous robot with real spatial awareness.

The system processes:
- Real-time 8x8 depth maps
- Obstacle distance
- Side clearance
- Ground proximity

Using this information, the robot dynamically:
- Moves forward
- Avoids obstacles
- Escapes trapped situations
- Performs autonomous recovery

---

# Features

- 🚗 Autonomous obstacle avoidance
- 📡 Real-time 8x8 depth sensing
- 🧠 Intelligent navigation logic
- ⚡ Differential motor steering
- 📊 Live terminal dashboard
- 🔥 Real-time sensor visualization
- 🛑 Escape & recovery mechanism
- 🚀 Fast reactive movement
- 🎯 Full-width field-of-view obstacle detection

---

# Hardware Used

| Component | Quantity |
|---|---|
| Raspberry Pi 5 | 1 |
| VL53L5CX ToF Sensor | 1 |
| L298N Motor Driver | 1 |
| DC Motors | 4 |
| Li-ion Battery Pack | 1 |
| Buck Converter | 1 |
| Jumper Wires | Multiple |

---

# Circuit Schematic

<p align="center">
  <img src="images/circuit.png" width="850"/>
</p>

<p align="center">
  <b>Complete Hardware Circuit Diagram of the Autonomous Robot</b>
</p>

---

# Process Flowchart

<p align="center">
  <img src="images/process.png" width="850"/>
</p>

<p align="center">
  <b>Autonomous Navigation and Obstacle Avoidance Flowchart</b>
</p>

---

# How It Works

The VL53L5CX sensor generates an **8x8 depth map** containing 64 individual distance readings in real time.

The robot continuously analyzes:
- Near obstacles
- Far obstacles
- Left-side clearance
- Right-side clearance

Based on the available free space, the robot decides whether to:
- Move forward
- Turn left
- Turn right
- Reverse and escape

---

# Navigation Logic

## Normal Driving
If no obstacle is detected:
- Robot moves forward continuously

## Obstacle Avoidance
If an obstacle appears:
- Robot compares left and right side clearance
- Chooses the safer direction
- Performs avoidance turn

## Escape Recovery
If the robot gets trapped:
- Reverse motion activates
- Robot performs a large escape turn
- Navigation resumes automatically

---

# Real-Time Dashboard

The project includes a terminal-based live dashboard showing:

- 8x8 depth matrix
- Robot state
- Navigation status
- Obstacle warnings

---

# Color Indicators

| Color | Meaning |
|---|---|
| 🔴 Red | Critical obstacle |
| 🟡 Yellow | Warning zone |
| 🟢 Green | Clear path |

---

# Pin Configuration

```python
LPN_PIN = 23

IN1 = 17
IN2 = 27
IN3 = 22
IN4 = 24

ENA = 18
ENB = 19
```

---

# Threshold Configuration

```python
THRESHOLD_NEAR = 150
THRESHOLD_FAR  = 300
MAX_DIST       = 2000
```

---

# Speed Configuration

```python
DRIVE_SPEED = 100
TURN_SPEED  = 80
LOOP_HZ     = 20
TURN_DURATION = 0.4
```

---

# Software Architecture

## Main Modules

- GPIO Initialization
- VL53L5CX Sensor Interface
- Motor Driver Control
- Obstacle Detection Engine
- Escape Recovery System
- Real-Time Dashboard UI

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Arijit1080/vl53l5cx-autonomous-car.git

cd vl53l5cx-autonomous-car
```

---

# Install Dependencies

```bash
pip install numpy lgpio
```

---

# Run the Program

```bash
python3 enhance.py
```

---

# Working Principle

```text
START
  ↓
Read 8x8 Sensor Matrix
  ↓
Detect Obstacles
  ↓
Compare Left & Right Clearance
  ↓
Choose Best Direction
  ↓
Move / Avoid / Escape
  ↓
Repeat
```

---

# Why VL53L5CX?

Unlike ultrasonic sensors, the VL53L5CX provides:

- 64 simultaneous depth zones
- Real spatial awareness
- Better obstacle detection
- Faster navigation decisions
- Reliable indoor robotics performance

This enables smoother and smarter autonomous navigation.

---

# Applications

- Autonomous robots
- Indoor navigation systems
- Robotics education
- AI navigation research
- Smart mobility projects
- Obstacle avoidance systems

---

# Future Improvements

- SLAM support
- ROS2 integration
- Camera fusion
- AI path planning
- Wireless telemetry
- Mapping & localization

---

# Project Demonstration

The robot can:
- Detect obstacles in real time
- Navigate autonomously
- Recover from trapped situations
- Move continuously without collisions

---

# Author

## Arijit Das


---

# License

This project is open-source under the MIT License.
