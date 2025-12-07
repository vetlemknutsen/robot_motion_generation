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

            print(f"IK target side={chain_name} pos={target.position} orient={target.orientation} base={base_frame} group=arm_torso")
            solution = moveit_ik.solve(target.position, target.orientation)
            print(f"IK solution joints={ {j: round(solution.get(j, 0), 3) for j in joints} }")
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

        for gripper in frame.grippers:
            gripper_config = config.get_gripper(gripper.side)
            if gripper_config:
                pos = gripper_config["closed"] if gripper.closed else gripper_config["open"]
                # Map side to prefix (right -> R, left -> L)
                side_prefix = gripper.side[0].upper() if gripper.side else ""
                gripper_moves = [
                    Move(side_prefix, joint, "", pos)
                    for joint in gripper_config["joints"]
                ]
                instructions.append(gripper_moves[0] if len(gripper_moves) == 1 else MultiMove(gripper_moves))

    return Program(motion.name, instructions)

def _split_joint_name(name: str) -> tuple[str, str]:
    side_prefix = name[0] if name and name[0] in ("L", "R") else ""
    core = name[len(side_prefix):]
    for suffix in AXIS_SUFFIXES:
        if core.endswith(suffix):
            return core[: -len(suffix)], suffix.lower()
    return core, ""
