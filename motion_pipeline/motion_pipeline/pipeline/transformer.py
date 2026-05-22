from motion_pipeline.types.TaskDescription import TaskDescription
from motion_pipeline.types.JointDescription import Move, MultiMove, JointDescription
from motion_pipeline.kinematics.base import IKSolver
from motion_pipeline.pipeline.configs.robot_config import RobotConfig


def taskdescription_to_jointdescription(motion: TaskDescription, config: RobotConfig, ik: IKSolver) -> JointDescription:
    instructions = []
    prev_joints = config.get_ik_seed() or None
    skipped = 0
    total = 0

    for frame in motion.frames:
        moves = []

        for target in frame.targets:
            total += 1
            orientations = [target.orientation] if target.orientation else config.get_orientation_options() or [None]
            trajectory = None

            for orient in orientations:
                position = [p - o for p, o in zip(target.position, config.base_offset)]
                try:
                    trajectory = ik.plan(position, orient, seed_state=prev_joints)
                except RuntimeError:
                    trajectory = None
                if trajectory:
                    break

            print(f"position: {target.position} solved: {str(trajectory is not None).lower()}")

            if not trajectory:
                skipped += 1
                continue

            prev_joints = trajectory[-1]
            if len(trajectory) == 1:
                for name in config.get_chain(target.side):
                    if name in trajectory[0]:
                        moves.append(Move(target.side, name, "", round(trajectory[0][name], 4)))
            else:
                for point in trajectory:
                    point_moves = []
                    for name in config.get_chain(target.side):
                        if name in point:
                            point_moves.append(Move(target.side, name, "", round(point[name], 4)))
                    if point_moves:
                        instructions.append(point_moves[0] if len(point_moves) == 1 else MultiMove(point_moves))

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
