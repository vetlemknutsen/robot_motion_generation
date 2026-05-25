from motion_pipeline.types.TaskDescription import TaskDescription
from motion_pipeline.types.JointDescription import Move, MultiMove, JointDescription
from motion_pipeline.kinematics.base import IKSolver
from motion_pipeline.pipeline.configs.robot_config import RobotConfig


def taskdescription_to_jointdescription(motion: TaskDescription, config: RobotConfig, ik: IKSolver) -> JointDescription:
    """Convert a task-space motion into a joint-space program via IK.
    Iterates over every frame and target, calling the IK solver. The
    previous successful solution is used as the seed for the next. Targets that can't
    be reached with any of the robot's allowed orientations are skipped.
    Args:
        motion: The TaskDescription to convert.
        config: The RobotConfig for the target robot (chains, grippers,
            base_offset, orientation options, etc.).
        ik: An IKSolver instance.
    Returns:
        Tuple of (JointDescription, skipped, total). skipped is the
        number of targets that failed IK; total is the number attempted.
    """
    instructions = []
    prev_joints = None # last successfull solution, used by IK seed for the next
    skipped = 0        # number of targets we couldn't reach
    total = 0          # total number of targets we tried

    for frame in motion.frames:
        moves = []

        for target in frame.targets:
            total += 1
            # If the target specifies an orientation, use only that
            # otherwise try the robot's list of fallback orientations
            # (some poses are only reachable from certain wrist angles)
            orientations = [target.orientation] if target.orientation else config.get_orientation_options() or [None]
            joints = None

            for orient in orientations:
                # convert world -> base by substracting the robot's base offset
                position = [p - o for p, o in zip(target.position, config.base_offset)]
                # seed with previous joints, solver finds a nearby solution
                joints = ik.try_solve(position, orient, seed_state=prev_joints)
                if not joints:
                    print(f"Position {target.position} not reachable, skipping frame")
                else:
                    print(f"Solved for position {target.position}")
                    prev_joints = joints
                    break

            # IK gave up on every orientation, skip this target
            if not joints:
                skipped += 1
                print(f"IK failed for {target.position}, skipping frame")
                continue

            # keep only the joints that belong to this arm's chain
            for name in config.get_chain(target.side):
                if name in joints:
                    moves.append(Move(target.side, name, "", round(joints[name], 4)))

        # keep only the joints that belong to this arm's chain
        if moves:
            instructions.append(moves[0] if len(moves) == 1 else MultiMove(moves))

        # handle gripper open/close commands the same way
        for grip in frame.grippers:
            gripper_config = config.get_gripper(grip.side)
            if gripper_config:
                val = gripper_config["closed"] if grip.closed else gripper_config["open"]
                gripper_moves = []
                # a gripper often has multiple joints for end effector
                for j in gripper_config["joints"]:
                    gripper_moves.append(Move(grip.side, j, "", val))
                instructions.append(gripper_moves[0] if len(gripper_moves) == 1 else MultiMove(gripper_moves))

    return JointDescription(motion.name, instructions), skipped, total
