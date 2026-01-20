import rclpy
from typing import Dict, Optional, Sequence

from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from moveit_msgs.srv import GetPositionIK
from builtin_interfaces.msg import Duration

class MoveItIKClient:
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
        avoid_collisions: bool = False,
        seed_state: Dict[str, float] = None
    ):
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
        req.ik_request.avoid_collisions = avoid_collisions
        # currently give MoveIt 2 seconds to solve
        req.ik_request.timeout = Duration(sec=1, nanosec=0)
        future = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self.node, future)
        res = future.result()
        if res.error_code.val != res.error_code.SUCCESS:
            raise RuntimeError(f"IK failed {res.error_code.val}")
        return dict(zip(res.solution.joint_state.name, res.solution.joint_state.position))

    def try_solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        avoid_collisions: bool = False,
        seed_state: Dict[str, float] = None,
    ) -> Optional[Dict[str, float]]:
        try:
            return self.solve(position, orientation, avoid_collisions, seed_state)
        except RuntimeError:
            return None
