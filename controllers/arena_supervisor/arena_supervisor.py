from controller import Supervisor
import math

robot = Supervisor()
timestep = int(robot.getBasicTimeStep())

# Link to the robot using the DEF name you just set
dog = robot.getFromDef("GhostDog")
arena = robot.getFromDef("circle_arena")

if dog:
    dog_trans = dog.getField("translation")
    # arena_radius = arena.getField("radius").getSFFloat() # Use if arena exists
    SAFE_RADIUS = 1.3 # Manually set safe zone

    while robot.step(timestep) != -1:
        pos = dog_trans.getSFVec3f()
        dist = math.sqrt(pos[0]**2 + pos[1]**2)

        if dist > SAFE_RADIUS:
            # Gentle push-back factor (0.98) to keep the dog stable
            new_pos = [pos[0] * 0.98, pos[1] * 0.98, pos[2]]
            dog_trans.setSFVec3f(new_pos)
else:
    print("ERROR: Could not find DEF 'GhostDog' in Scene Tree.")