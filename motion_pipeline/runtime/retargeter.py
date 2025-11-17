from math import radians

from motion_pipeline.core.canonical import CanonicalMotion
from motion_pipeline.core.schema import Move, MultiMove, Program


def motion_to_program(motion: CanonicalMotion) -> Program:
    frames = sorted(motion.frames, key=lambda f: f.time)
    instructions = []
    for frame in frames:
        moves = [
            Move(angle.side, angle.joint, angle.component, round(radians(angle.degrees),2))
            for angle in frame.joint_angles
        ]
        if not moves:
            continue
        instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))
    return Program(motion.name, instructions)


directive_to_program = motion_to_program
