import time
from typing import Dict, List, Optional, Sequence

from rclpy.callback_groups import ReentrantCallbackGroup
from geometry_msgs.msg import PoseStamped
from moveit_msgs.msg import Constraints, JointConstraint
from moveit_msgs.srv import GetMotionPlan, GetPositionIK
from builtin_interfaces.msg import Duration

from motion_pipeline.kinematics.base import IKSolver


class MoveItIKClient(IKSolver):
    def __init__(self, node, group_name: str, base_frame: str, ee_link: str):
        self.group_name = group_name
        self.base_frame = base_frame
        self.ee_link = ee_link
        self.node = node
        self.cb_group = ReentrantCallbackGroup()
        self.cli = self.node.create_client(GetPositionIK, "/compute_ik", callback_group=self.cb_group)
        self.plan_cli = None
        self.cli.wait_for_service()

    def solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Dict[str, float] = None,
    ) -> Dict[str, float]:
        req = GetPositionIK.Request()
        req.ik_request.group_name = self.group_name
        req.ik_request.ik_link_name = self.ee_link
        req.ik_request.pose_stamped = PoseStamped()
        req.ik_request.pose_stamped.header.frame_id = self.base_frame
        req.ik_request.pose_stamped.pose.position.x = position[0]
        req.ik_request.pose_stamped.pose.position.y = position[1]
        req.ik_request.pose_stamped.pose.position.z = position[2]

        if orientation:
            req.ik_request.pose_stamped.pose.orientation.x = orientation[0]
            req.ik_request.pose_stamped.pose.orientation.y = orientation[1]
            req.ik_request.pose_stamped.pose.orientation.z = orientation[2]
            req.ik_request.pose_stamped.pose.orientation.w = orientation[3]

        if seed_state:
            req.ik_request.robot_state.joint_state.name = list(seed_state.keys())
            req.ik_request.robot_state.joint_state.position = list(seed_state.values())
            req.ik_request.robot_state.is_diff = True

        req.ik_request.avoid_collisions = False
        req.ik_request.timeout = Duration(sec=1, nanosec=0)

        future = self.cli.call_async(req)
        while not future.done():
            time.sleep(0.01)
        res = future.result()

        if res.error_code.val != res.error_code.SUCCESS:
            raise RuntimeError(f"IK failed {res.error_code.val}")

        return dict(zip(res.solution.joint_state.name, res.solution.joint_state.position))

    def plan(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Optional[Dict[str, float]] = None,
    ) -> List[Dict[str, float]]:
        if self.plan_cli is None:
            self.plan_cli = self.node.create_client(GetMotionPlan, "/plan_kinematic_path", callback_group=self.cb_group)
            self.plan_cli.wait_for_service()

        goal_joints = self.solve(position, orientation, seed_state)

        req = GetMotionPlan.Request()
        req.motion_plan_request.group_name = self.group_name
        req.motion_plan_request.allowed_planning_time = 2.0
        req.motion_plan_request.num_planning_attempts = 3
        req.motion_plan_request.max_velocity_scaling_factor = 1.0
        req.motion_plan_request.max_acceleration_scaling_factor = 1.0

        req.motion_plan_request.start_state.is_diff = True
        if seed_state:
            req.motion_plan_request.start_state.joint_state.name = list(seed_state.keys())
            req.motion_plan_request.start_state.joint_state.position = list(seed_state.values())

        constraints = Constraints()
        for joint_name, joint_pos in goal_joints.items():
            joint_constraint = JointConstraint()
            joint_constraint.joint_name = joint_name
            joint_constraint.position = float(joint_pos)
            joint_constraint.tolerance_above = 1e-3
            joint_constraint.tolerance_below = 1e-3
            joint_constraint.weight = 1.0
            constraints.joint_constraints.append(joint_constraint)
        req.motion_plan_request.goal_constraints = [constraints]

        future = self.plan_cli.call_async(req)
        while not future.done():
            time.sleep(0.01)
        res = future.result()

        if not res:
            return [goal_joints]

        plan_res = res.motion_plan_response
        if plan_res.error_code.val != plan_res.error_code.SUCCESS:
            return [goal_joints]

        trajectory = plan_res.trajectory.joint_trajectory
        if not trajectory.points:
            return [goal_joints]

        return [dict(zip(trajectory.joint_names, point.positions)) for point in trajectory.points]
