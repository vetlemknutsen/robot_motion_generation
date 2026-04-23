from motion_pipeline.core.task_level import TaskDescription
from motion_pipeline.core.joint_level import Move, MultiMove, JointDescription
from motion_pipeline.kinematics.base import IKSolver
from motion_pipeline.runtime.configs.robot_config import RobotConfig


def taskdescription_to_jointdescription(motion: TaskDescription, config: RobotConfig, ik: IKSolver) -> JointDescription:
    instructions = []
    prev_joints = None
    skipped = 0
    total = 0

    for frame in motion.frames:
        moves = []

        for target in frame.targets:
            total += 1
            # Try different orientations until IK succeeds
            orientations = [target.orientation] if target.orientation else config.get_orientation_options() or [None]
            joints = None

            for orient in orientations:
                position = [p - o for p, o in zip(target.position, config.base_offset)]
                joints = ik.try_solve(position, orient, seed_state=prev_joints)
                if not joints:
                    print(f"Position {target.position} not reachable, skipping frame")
                else:
                    print(f"Solved for position {target.position}")
                    prev_joints = joints
                    break


            if not joints:
                skipped += 1
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

    return JointDescription(motion.name, instructions), skipped, total
