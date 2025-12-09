import os
from math import radians
from motion_pipeline.core.motion import MotionSequence
from motion_pipeline.core.schema import Move, MultiMove, Program
from motion_pipeline.runtime.moveit_ik import MoveItIKClient
from motion_pipeline.runtime.robot_config import RobotConfig


def motion_to_program(motion: MotionSequence, config: RobotConfig) -> Program:
    """Convert a motion sequence to a robot program using IK."""
    instructions = []
    ik_client = None

    for frame in motion.frames:
        moves = []

        # Process end-effector targets with IK
        for target in frame.targets:
            if ik_client is None:
                _, tip = config.get_end_effector(target.side)
                ik_client = MoveItIKClient(
                    group_name="arm_torso",
                    base_frame=os.getenv("MOVEIT_PLANNING_FRAME", "base_footprint"),
                    ee_link=tip
                )

            orientations = [target.orientation] if target.orientation else config.get_orientation_options() or [None]
            solution = None
            for orient in orientations:
                solution = ik_client.try_solve(target.position, orient)
                if solution:
                    break

            if not solution:
                raise RuntimeError(f"IK failed at {target.position}")

            for joint in config.get_chain(target.side):
                if joint in solution:
                    pos = config.clamp_joint(joint, solution[joint])
                    moves.append(Move(target.side, joint, "", round(pos, 4)))

        for angle in frame.joint_angles:
            moves.append(Move(angle.side, angle.joint, angle.component, round(radians(angle.degrees), 2)))

        if moves:
            instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))

        for gripper in frame.grippers:
            gcfg = config.get_gripper(gripper.side)
            if gcfg:
                pos = gcfg["closed"] if gripper.closed else gcfg["open"]
                prefix = gripper.side[0].upper()
                gmoves = [Move(prefix, j, "", pos) for j in gcfg["joints"]]
                instructions.append(gmoves[0] if len(gmoves) == 1 else MultiMove(gmoves))

    return Program(motion.name, instructions)
