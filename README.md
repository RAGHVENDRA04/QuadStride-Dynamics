"# QuadStride-Dynamics" 


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](https://www.python.org/)
[![Webots](https://img.shields.io/badge/Webots-R2023b-orange.svg)](https://cyberbotics.com/)

> *A Physics-Aware Autonomous Quadruped Navigator for Constrained Circular Environments*

---

## 🎥 Project Demo

https://github.com/user-attachments/assets/bb1d13ec-8491-4536-990c-ef4c5ca195e6
```
![BalanceBot Demo](assets/demo.gif)
```

*BalanceBot navigating a circular arena with dynamic stability compensation*

---

## 📖 Overview

**BalanceBot Apex** is an advanced quadruped simulation project that solves one of robotics' most challenging problems: **maintaining stability in tight, circular arenas where centrifugal forces cause catastrophic flipping**.

Traditional quadruped gaits fail in constrained rotational environments. This project introduces a **Stability Governor** system that dynamically adjusts gait parameters based on real-time IMU data, preventing the "Centrifugal Death Spiral" through intelligent physics compensation.

### 🎯 Key Innovation

The **Active Roll Compensation (ARC)** system monitors body tilt and automatically triggers three simultaneous responses:
- **Dynamic Crouching** - Lowers center of mass by 54%
- **Stance Narrowing** - Reduces tipping lever-arm
- **Turn Braking** - Cuts yaw velocity by 65%

---

## 🏗️ System Architecture

### Control Loop Pipeline

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Sensors   │────▶│  Stability   │────▶│    Gait     │
│  - IMU      │     │  Governor    │     │   Engine    │
│  - ToF      │     │  (ARC)       │     │  (Trot)     │
│  - Distance │     └──────────────┘     └─────────────┘
└─────────────┘            │                     │
                           ▼                     ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  Physics    │     │   Motor     │
                    │  Bracing    │     │  Commands   │
                    └─────────────┘     └─────────────┘
```

### Stability Governor Logic

The core innovation monitors **Body Roll** angles from the IMU:

```python
if abs(roll_angle) > CRITICAL_THRESHOLD:  # 12-15°
    activate_physics_brace()
    lower_center_of_mass()
    narrow_stance_width()
    reduce_turn_velocity()
```

---

## 🔬 Technical Deep Dive

### The "Round Arena" Challenge

In circular arenas, continuous rotation generates centrifugal force:

```
F_c = m * v² / r
```

Where:
- `m` = robot mass
- `v` = tangential velocity
- `r` = turn radius

For a large quadruped in a tight arena, this force creates a **tipping moment** around the outer legs.

### Physics-Based Solution

#### 1. Dynamic Center of Mass Adjustment

```python
# Normal Walking
amplitude = 0.82  # High stance

# Turn Detected
amplitude = 0.38  # Crouch: ↓54% height
```

Lower CoM reduces the tipping moment arm by moving the gravitational force vector closer to the support polygon.

#### 2. Stance Narrowing

```python
# Calculate tipping torque reduction
original_width = 0.45  # meters
narrow_width = 0.28    # meters

torque_reduction = (narrow_width / original_width) * 100
# Result: 38% reduction in destabilizing torque
```

By bringing legs toward centerline, we reduce the lever arm that centrifugal force acts upon.

#### 3. Adaptive Turn Braking

```python
if stability_at_risk:
    turn_speed *= 0.35  # 65% reduction
```

Reduces tangential velocity, directly decreasing centrifugal force.

---

## 🛠️ Technical Specifications

| Feature | Specification |
|---------|--------------|
| **Language** | Python 3.10+ |
| **Simulation Engine** | Webots R2023b |
| **Gait Type** | Asynchronous Trot (Sine-wave) |
| **Control Frequency** | 32 Hz |
| **Stability System** | Active Roll Compensation (ARC) |
| **Sensors** | IMU (Roll/Pitch/Yaw) + 5× Distance Sensors |
| **Critical Threshold** | 12-15° body roll |
| **Response Time** | < 32ms |

### Physics Parameters

```python
# Robot Configuration (Critical!)
centerOfMass: 0 0 -0.07
mass: 15.2 kg
floor_friction: 0.7

# Gait Parameters
stride_frequency: 2.2 Hz
leg_lift_height: 0.45 m
stance_phase_ratio: 0.6
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Webots R2023b** or later ([Download](https://cyberbotics.com/))
- **Python 3.10+** configured in Webots preferences

### Quick Start

**Step 1: Clone the Repository**

```bash
git clone https://github.com/yourusername/balancebot-apex.git
cd balancebot-apex
```

**Step 2: Open in Webots**

```bash
webots worlds/round_arena.wbt
```

**Step 3: Configure Robot Controller**

- Right-click Robot node → Controller → Select `ghostdog_walk.py`

**Step 4: Set Physics (Critical Step!)**

```
Robot → Physics → centerOfMass: 0 0 -0.07
WorldInfo → ContactProperties → coulombFriction: 0.7
```

**Step 5: Run Simulation**

- Press ▶️ Play button
- Monitor console for telemetry

---

## 📊 Telemetry & Debugging

The controller outputs real-time diagnostics every cycle:

```
═══════════════════════════════════════════════════════
[CYCLE 1247] BALANCEBOT TELEMETRY
═══════════════════════════════════════════════════════
ROLL:        -13.4° ⚠️  [THRESHOLD EXCEEDED]
PITCH:       2.1
