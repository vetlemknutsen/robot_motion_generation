import os
from motion_pipeline.core.task_level import Motion
from motion_pipeline.core.joint_level import Move, MultiMove, Program
from motion_pipeline.kinematics.base import IKSolver
from motion_pipeline.runtime.configs.robot_config import RobotConfig


def motion_to_program(motion: Motion, config: RobotConfig, ik: IKSolver) -> Program:
    instructions = []
    prev_joints = None

    for frame in motion.frames:
        moves = []

        for target in frame.targets:
            # Try different orientations until IK succeeds
            orientations = [target.orientation] if target.orientation else config.get_orientation_options() or [None]
            joints = None

            for orient in orientations:
                joints = ik.try_solve(target.position, orient, seed_state=prev_joints)
                if not joints:
                    print(f"IK failed for pos={target.position}, orient={orient}")
                else:
                    print(f"IK joints keys: {list(joints.keys())}")
                    prev_joints = joints
                    break


            if not joints:
                print(f"IK failed for {target.position}, skipping frame")
                continue

            for name in config.get_chain(target.side):
                if name in joints:
                    moves.append(Move(target.side, name, "", round(joints[name], 4)))

        if moves:
            instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))

        for grip in frame.grippers:
            gripper_config = config.get_gripper(grip.side)
            if gripper_config:
                val = gripper_config["closed"] if grip.closed else gripper_config["open"]
                gripper_moves = []
                for j in gripper_config["joints"]:
                    gripper_moves.append(Move(grip.side, j, "", val))
                instructions.append(gripper_moves[0] if len(gripper_moves) == 1 else MultiMove(gripper_moves))

    return Program(motion.name, instructions)
