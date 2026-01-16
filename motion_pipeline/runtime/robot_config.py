
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RobotConfig:
    # robot name
    name: str
    # for moveit ik solver
    moveit_group: str
    base_frame: str
    # which joint belong to each arm
    chains: dict = field(default_factory=dict)
    # limits for joint
    limits: dict = field(default_factory=dict)
    # workspace limits for end-effector position
    workspace_limits: dict = field(default_factory=dict)
    end_effectors: dict = field(default_factory=dict)
    grippers: dict = field(default_factory=dict)
    default_orientation: list = None
    orientation_options: list = None   

    def get_chain(self, name: str) -> List[str]:
        return self.chains.get(name, [])

    def get_end_effector(self, name: str) -> Tuple[str, str]:
        return self.end_effectors[name]

    def clamp_joint(self, joint_name: str, value: float) -> float:
        if joint_name in self.limits:
            lo, hi = self.limits[joint_name]
            return max(lo, min(hi, value))
        return value

    def clamp_position(self, axis: str, value: float) -> float:
        if axis in self.workspace_limits:
            lo, hi = self.workspace_limits[axis]
            return max(lo, min(hi, value))
        return value

    def get_gripper(self, side: str) -> dict:
        return self.grippers.get(side, {})

    def get_default_orientation(self):
        return self.default_orientation

    def get_orientation_options(self):
        if self.orientation_options:
            return self.orientation_options
        if self.default_orientation:
            return [self.default_orientation]
        return None
    
    def get_group_name(self):
        return self.moveit_group

    def get_base_frame(self):
        return self.base_frame
