# EdgeCV-Distress-Alert-System 🚨

An automated, edge-computing public safety system designed to recognize the universal **"Signal for Help"** distress gesture using Computer Vision and physical hardware actuation. 

This project implements a multi-signal temporal state machine to filter out accidental false positives, extracts live geolocation data upon trigger confirmation, and alerts local hardware via serial communication.

---

## 🏗️ System Architecture

1. **Vision Layer (MediaPipe & OpenCV)**: Extracts 21 hand landmarks and calculates normalized Euclidean distances to evaluate hand geometry independently of spatial orientation (supports left/right hands and multiple angles).
2. **Temporal State Machine**: Monitors gesture state changes, requiring the distress sequence (thumb tucked, fingers folded over) to be executed and released 3 times within a rolling 6-second window.
3. **Emergency Telemetry Pipeline**: Automatically pings a networking geolocation service to pack approximate coordinates (Latitude/Longitude) into an outbound SOS dispatch payload containing a live Google Maps link.
4. **Physical Actuation Layer**: Transmits binary alert flags over serial protocol (`/dev/ttyUSB0`) to an external microcontroller (Arduino Uno/CH340) to drive a high-frequency physical strobe light distress beacon.

---

## 🚀 Getting Started

### Prerequisites

* Ubuntu/Linux environment (or Windows Subsystem for Linux - WSL2)
* Python 3.10+
* Arduino IDE (for flashing the microcontroller)

### Hardware Components
* Arduino Uno (or any ATmega328P compatible board with a CH340 serial chip)
* USB Type-B interface cable

### Installation & Execution

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/EdgeCV-Distress-Alert-System.git](https://github.com/YOUR_USERNAME/EdgeCV-Distress-Alert-System.git)
   cd EdgeCV-Distress-Alert-System
