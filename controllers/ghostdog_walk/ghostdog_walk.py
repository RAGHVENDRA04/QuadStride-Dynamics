from controller import Robot
import math

# --- INITIALIZATION ---
robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Hardware Setup
motor_names = ["hip0", "hip1", "hip2", "hip3", "spine"]
motors = [robot.getDevice(n) for n in motor_names]
ps_head = robot.getDevice("ps_head")
sensor_names = ["ps_fl", "ps_bl", "ps_fr", "ps_br"]
feet_sensors = [robot.getDevice(n) for n in sensor_names]
imu = robot.getDevice("inertial unit")

# Enable devices
for s in [ps_head, imu] + feet_sensors:
    if s: s.enable(timestep)

# ELITE PARAMETERS
freq, t = 1.3, 0.0
smooth_ampl = 0.0
recovery_timer = 0.0
RECOVERY_TIME_LIMIT = 1.6 
push_away_offset = 0.0
lap_counter = 0
distance_travelled = 0.0

print("--- GHOSTDOG ELITE: FULL AUTONOMOUS PATROL ENGAGED ---")

while robot.step(timestep) != -1:
    # 1. STANDING WARMUP (3s)
    if t < 3.0:
        for m in motors[0:4]: m.setPosition(-0.1)
        t += timestep / 1000.0
        continue

    # 2. SENSOR ANALYSIS & ELITE FILTERING
    v_h = ps_head.getValue() if ps_head else 0
    real_h = v_h if v_h < 980 else 0 
    
    phase = t * 2 * math.pi * freq
    foot_blocked = False
    active_sensor = "None"
    
    # Check feet only during ground-contact phase with higher 250 threshold
    for i, s in enumerate(feet_sensors):
        if s:
            val = s.getValue()
            leg_phase = phase if i in [0, 3] else (phase + math.pi)
            if math.sin(leg_phase) < -0.2 and 250 < val < 980:
                foot_blocked = True
                active_sensor = sensor_names[i]
                break

    # 3. ELITE COORDINATION & STANCE NARROWING
    if real_h > 150 or foot_blocked:
        recovery_timer = RECOVERY_TIME_LIMIT
    
    if recovery_timer > 0:
        # AVOIDANCE: Pivot sharply (0.40) while narrowing stance
        target_turn = 0.40 
        target_ampl = 0.42 
        # Reduced push-away offset (0.10) to stop extreme lean
        push_away_offset = -0.10 if active_sensor in ["ps_fr", "ps_br"] or real_h > 180 else 0.10
        l_speed = 0.3 if push_away_offset > 0 else 1.6
        r_speed = 1.6 if push_away_offset > 0 else 0.3
        recovery_timer -= timestep / 1000.0
    else:
        # COMFORT: Full leg extension
        target_turn = 0.0
        target_ampl = 0.82 
        l_speed, r_speed = 1.0, 1.0
        push_away_offset *= 0.8 # Smooth decay

    # 4. GAIT CALCULATION
    if smooth_ampl < target_ampl: smooth_ampl += 0.015 
    elif smooth_ampl > target_ampl: smooth_ampl -= 0.015

    s1 = smooth_ampl * 0.35 * math.sin(phase)
    s2 = smooth_ampl * 0.35 * math.sin(phase + math.pi)

    # 5. APPLY COORDINATED ANGLES WITH STANCE NARROWING
    if all(motors):
        # Stance narrowing pulls legs under body to prevent tail-swiping
        narrowing = push_away_offset * 0.6 
        
        pos_fl = (s1 + 0.15 + push_away_offset) * l_speed
        pos_fr = (-s2 + 0.15 + push_away_offset) * r_speed
        pos_bl = (s2 - 0.15 + narrowing) * l_speed
        pos_br = (-s1 - 0.15 + narrowing) * r_speed
        
        motors[0].setPosition(pos_fl) 
        motors[1].setPosition(pos_bl) 
        motors[2].setPosition(pos_fr) 
        motors[3].setPosition(pos_br) 
        motors[4].setPosition(target_turn)

    # 6. DEEP DEBUGGING & PATROL LOGS
    if t % 0.8 < 0.05:
        roll = math.degrees(imu.getRollPitchYaw()[0]) if imu else 0
        state = "RECOVERING" if recovery_timer > 0 else "NORMAL"
        distance_travelled += 0.1 * smooth_ampl # Estimated patrol distance
        
        print(f"\n--- ELITE PATROL REPORT [{t:.2f}s] ---")
        print(f"STATUS: {state} | BODY ROLL: {roll:+.1f}°")
        print(f"DIAG: Amp:{smooth_ampl:.2f} | Turn:{target_turn:.2f} | Side_Shift:{push_away_offset:.2f}")
        print(f"HIPS: FL:{pos_fl:+.2f} | FR:{pos_fr:+.2f} | BL:{pos_bl:+.2f} | BR:{pos_br:+.2f}")
        print(f"CLEARANCE: Pair1:{(s1+0.15):.3f}m | Obstacle: {active_sensor}")
        print(f"EST. PATROL DISTANCE: {distance_travelled:.2f}m")
        print("-" * 50)

    t += timestep / 1000.0