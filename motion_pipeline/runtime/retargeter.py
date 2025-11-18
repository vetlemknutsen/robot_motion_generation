from math import degrees, radians

from motion_pipeline.core.motion import MotionSequence, JointAngle
from motion_pipeline.core.schema import Move, MultiMove, Program


YAW_CANON = 90
PITCH_CANON = 60
# NAO limits (radians).
NAO_YAW = 2.09
NAO_PITCH_MIN = -0.67
NAO_PITCH_MAX = 0.51


def motion_to_program(motion: MotionSequence) -> Program:
    frames = sorted(motion.frames, key=lambda f: f.time)
    instructions = []
    for frame in frames:
        moves = []
        for angle in frame.joint_angles:
            # Map to NAO-specific head angles
            mapped = _map_head(angle)
            moves.append(Move(mapped.side, mapped.joint, mapped.component, round(radians(mapped.degrees), 2)))
        if moves:
            instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))
    return Program(motion.name, instructions)


def _map_head(angle: JointAngle) -> JointAngle:
    if angle.component == "yaw":
        # Clamp yaw to -90 and 90 degrees
        value = max(-YAW_CANON, min(YAW_CANON, angle.degrees))
        # Normalize to [-1, 1]
        normalized = value / YAW_CANON if YAW_CANON else 0
        return JointAngle(angle.joint, angle.component, degrees(normalized * NAO_YAW), angle.side)
    if angle.component == "pitch":
        # Clamp pitch to -60 and 60 degrees
        value = max(-PITCH_CANON, min(PITCH_CANON, angle.degrees))
        # Normalize
        normalized = value / PITCH_CANON if PITCH_CANON else 0
        # Map [-1,1] to [0,1]
        ratio = (normalized + 1) / 2
        pitch = NAO_PITCH_MIN + ratio * (NAO_PITCH_MAX - NAO_PITCH_MIN)
        return JointAngle(angle.joint, angle.component, degrees(pitch), angle.side)
    return angle

