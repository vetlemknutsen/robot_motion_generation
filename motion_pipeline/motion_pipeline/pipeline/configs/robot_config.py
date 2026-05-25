
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RobotConfig:
    """
    Configuration for a robot in the pipeline. 
    Information the IK solver needs for the specific robot. 
    (Some things could be extracted from URDF by parsing, kept simple here)

    To add a new robot, create a YAML file in configs/robots/
    It will be auto-discovered by the pipeline
    """
    name: str                   # display name, for example "NAO", "TIAGo"
    moveit_group: str           # MoveIt planning group, for example "right_arm" 
    base_frame: str             # transformation base frame, for example "base_link"

    chains: dict = field(default_factory=dict)           # joints per side, {"right": ["joint1", "joint2", ...]}
    end_effectors: dict = field(default_factory=dict)    # (base_link, tip_link) per side for IK, {"right": ("base_link", "r_wrist")}
    grippers: dict = field(default_factory=dict)         # gripper joints + open/close per side
    default_orientation: list = None                     # default end-effector orientation
    orientation_options: list = None                     # list of orientations to try if IK fails with default
    base_offset: list = field(default_factory=lambda: [0.0, 0.0, 0.0])  # offset from world frame to base_frame
    ik_seed: dict = field(default_factory=dict)

    # Nested dict that maps a joint to its human-readable category
    # Lets us emit RML like "move right shoulder pitch ..." instead of raw joint names
    joint_groups: dict = field(default_factory=dict)
    
    # reverse lookup: joint_name -> (side, group, orientation)
    joint_map: dict = field(default_factory=dict, init=False)

    # flip joint groups inside-out so we can look things up by joint name
    def __post_init__(self):
        for side, groups in self.joint_groups.items():
            for group_name, rotations in groups.items():
                for rotation, joint_name in rotations.items():
                    self.joint_map[joint_name] = (side, group_name, rotation)

    # The getters below are thing wrappers so callers don't poke at the dicts directly
    def get_chain(self, name: str) -> List[str]:
        return self.chains.get(name, [])

    def get_end_effector(self, name: str) -> Tuple[str, str]:
        return self.end_effectors[name]

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

    def get_ik_seed(self) -> dict: 
        return self.ik_seed