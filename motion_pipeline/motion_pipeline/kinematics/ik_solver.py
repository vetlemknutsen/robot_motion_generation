import rclpy
from typing import Dict, Optional, Sequence

from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from moveit_msgs.srv import GetPositionIK
from builtin_interfaces.msg import Duration

from motion_pipeline.kinematics.base import IKSolver

class MoveItIKClient(IKSolver):
    def __init__(self, group_name: str, base_frame: str, ee_link: str):
        self.group_name = group_name
        self.base_frame = base_frame
        self.ee_link = ee_link
        self.node = Node("motion_pipeline_ik_client")
        self.cli = self.node.create_client(GetPositionIK, "/compute_ik")
        self.cli.wait_for_service()

    # call IK
    def solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Dict[str, float] = None
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
        else:
            req.ik_request.robot_state.joint_state.name = []
            req.ik_request.robot_state.joint_state.position = []

        req.ik_request.avoid_collisions = False
        # currently give MoveIt 1 second to solve
        req.ik_request.timeout = Duration(sec=1, nanosec=0)

        self.node.get_logger().info(
            f"IK request: group={self.group_name}, ee_link={self.ee_link}, "
            f"frame={self.base_frame}, pos={list(position)}, "
            f"orient={list(orientation) if orientation else None}, "
            f"seed_joints={list(seed_state.keys()) if seed_state else None}"
        )

        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        res = future.result()

        if res is None:
            raise RuntimeError("IK service call returned None (timeout or service unavailable)")

        if res.error_code.val != res.error_code.SUCCESS:
            self.node.get_logger().warn(
                f"IK failed: error_code={res.error_code.val}, "
                f"solution_joints={list(res.solution.joint_state.name)}, "
                f"solution_positions={list(res.solution.joint_state.position)}"
            )
            raise RuntimeError(f"IK failed {res.error_code.val}")

        self.node.get_logger().info(f"IK solved: {list(res.solution.joint_state.name)}")
        return dict(zip(res.solution.joint_state.name, res.solution.joint_state.position))
