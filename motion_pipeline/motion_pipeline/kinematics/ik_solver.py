import time

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from typing import Dict, Optional, Sequence

from geometry_msgs.msg import PoseStamped
from moveit_msgs.srv import GetPositionIK
from builtin_interfaces.msg import Duration

from motion_pipeline.kinematics.base import IKSolver


class MoveItIKClient(IKSolver):
    def __init__(self, node, group_name: str, base_frame: str, ee_link: str):
        self.group_name = group_name # which planning group, e.g. "right_arm"
        self.base_frame = base_frame # frame the target position is relative to
        self.ee_link = ee_link         # the end-effector link we want to move
        self.node = node
        # reentrant so this service call can run while other callbacks are active
        self.cb_group = ReentrantCallbackGroup()
        # connect to MoveIt's IK service and wait until it's up
        self.cli = self.node.create_client(GetPositionIK, "/compute_ik", callback_group=self.cb_group)
        self.cli.wait_for_service()

    # build a MoveIt IK Request and return the joint positions it solved for
    def solve(
        self,
        position: Sequence[float],
        orientation: Optional[Sequence[float]] = None,
        seed_state: Dict[str, float] = None
    ) -> Dict[str, float]:
        """Solve inverse kinematics for one end-effector pose.
        Args:
            position: Target [x, y, z] in meters, in the robot's base frame.
            orientation: Optional quaternion [x, y, z, w]. If None, the
                solver is free to pick any orientation.
            seed_state: Optional dict of {joint_name: angle} used as a
                starting guess. Passing the previous solution makes motion
                smoother and IK faster.
        Returns:
            Dict mapping joint names to joint angles in radians.
        Raises:
            RuntimeError: If no solution is found.
        """
        req = GetPositionIK.Request()
        req.ik_request.group_name = self.group_name
        req.ik_request.ik_link_name = self.ee_link
        # fill in the target pose
        req.ik_request.pose_stamped = PoseStamped()
        req.ik_request.pose_stamped.header.frame_id = self.base_frame
        req.ik_request.pose_stamped.pose.position.x = position[0]
        req.ik_request.pose_stamped.pose.position.y = position[1]
        req.ik_request.pose_stamped.pose.position.z = position[2]
        # if we got orientation, set it. 
        if orientation:
            req.ik_request.pose_stamped.pose.orientation.x = orientation[0]
            req.ik_request.pose_stamped.pose.orientation.y = orientation[1]
            req.ik_request.pose_stamped.pose.orientation.z = orientation[2]
            req.ik_request.pose_stamped.pose.orientation.w = orientation[3]
        # seed_state is the starting guess for the solver. Using the previous
        # solution helps IK find a nearby answer.
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

        # send the request and wait for the response
        future = self.cli.call_async(req)
        while not future.done():
            time.sleep(0.01)
        res = future.result()
        if res.error_code.val != res.error_code.SUCCESS:
            raise RuntimeError(f"IK failed {res.error_code.val}")
        # return as {joint_name: angle} 
        return dict(zip(res.solution.joint_state.name, res.solution.joint_state.position))
