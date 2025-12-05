import os
from math import radians
from typing import Optional
from motion_pipeline.core.motion import MotionSequence, JointAngle
from motion_pipeline.core.schema import Move, MultiMove, Program
from motion_pipeline.runtime.moveit_ik import MoveItIKClient
from motion_pipeline.runtime.robot_config import RobotConfig

# Currently kind of hardcoded for Tiago Steel

AXIS_SUFFIXES = ("Roll", "Pitch", "Yaw")

def motion_to_program(motion: MotionSequence, config: RobotConfig) -> Program:
    # sort frames by time for correct order
    frames = sorted(motion.frames, key=lambda f: f.time)
    instructions = []
    moveit_ik: Optional[MoveItIKClient] = None

    for frame in frames:
        moves = []

        # run ik for end-effector targets
        for target in frame.targets:
            chain_name = target.side
            joints = config.get_chain(chain_name)
            if moveit_ik is None:
                base_frame = os.getenv("MOVEIT_PLANNING_FRAME", "base_footprint")
                _, tip_link = config.get_end_effector(chain_name)
                moveit_ik = MoveItIKClient(group_name="arm_torso", base_frame=base_frame, ee_link=tip_link)

            solution = moveit_ik.solve(target.position, target.orientation)
            for joint_full in joints:
                if joint_full not in solution:
                    continue
                pos = config.clamp_joint(joint_full, solution[joint_full])
                joint, rotation = _split_joint_name(joint_full)
                moves.append(Move(chain_name, joint, rotation, round(pos, 4)))

        for angle in frame.joint_angles:
            moves.append(Move(angle.side, angle.joint, angle.component, round(radians(angle.degrees), 2)))

        if moves:
            instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))

    return Program(motion.name, instructions)

def _split_joint_name(name: str) -> tuple[str, str]:
    side_prefix = name[0] if name and name[0] in ("L", "R") else ""
    core = name[len(side_prefix):]
    for suffix in AXIS_SUFFIXES:
        if core.endswith(suffix):
            return core[: -len(suffix)], suffix.lower()
    return core, ""
