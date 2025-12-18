from controller import Supervisor
import math

# -----------------------------
# Supervisor Init
# -----------------------------
robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# -----------------------------
# Nodes & Setup
# -----------------------------
dog = robot.getFromDef("GhostDog")
arena = robot.getFromDef("circleArena")

# Get Arena Radius
if arena:
    arena_radius = arena.getField("radius").getSFFloat()
else:
    arena_radius = 2.0

# Get Boxes
boxes = [robot.getFromDef(f"wooden box({i})") for i in range(1, 5)]
boxes = [b for b in boxes if b is not None]

dog_translation = dog.getField("translation")

# -----------------------------
# Motors
# -----------------------------
motor_names = ["hip0", "hip1", "hip2", "hip3", "spine"]
motors = [robot.getDevice(name) for name in motor_names]

# -----------------------------
# Parameters & Limits
# -----------------------------
freq = 1.7
ampl = 0.9
t = 0.0

# PHYSICAL LIMITS (Adjusted to stop the warnings)
MAX_SPINE_ANGLE = 0.58  # Staying just under the 0.6 limit
SAFE_MARGIN = arena_radius - 0.25
BOX_AVOID_DIST = 0.35

print("🐕 SMART PATROL PUPPY: LIMITS APPLIED")

# -----------------------------
# Main Loop
# -----------------------------
while robot.step(timestep) != -1:

    pos = dog_translation.getSFVec3f()
    x, y = pos[0], pos[1]
    dist_from_center = math.sqrt(x*x + y*y)

    # Reset spine to straight by default
    target_spine = 0.0

    # 1. Boundary Check (Circle)
    if dist_from_center > SAFE_MARGIN:
        target_spine = -MAX_SPINE_ANGLE  # Turn back inside

    # 2. Box Check (Overwrites boundary check if close to box)
    for box in boxes:
        bpos = box.getField("translation").getSFVec3f()
        d = math.sqrt((x - bpos[0])**2 + (y - bpos[1])**2)
        if d < BOX_AVOID_DIST:
            target_spine = MAX_SPINE_ANGLE  # Turn away
            break

    # 3. Quadruped Gait Calculation
    phase = t * 2.0 * math.pi * freq
    fpos = ampl * 0.4 * math.sin(phase) + 0.05
    hpos = ampl * 0.6 * math.sin(phase + 2.0) - 0.15

    # 4. Actuation
    if all(motors):
        motors[0].setPosition(fpos)
        motors[2].setPosition(fpos)
        motors[1].setPosition(hpos)
        motors[3].setPosition(hpos)
        # Apply the clamped spine angle
        motors[4].setPosition(target_spine)

    t += timestep / 1000.0