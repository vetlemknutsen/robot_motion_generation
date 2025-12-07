
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RobotConfig:
    # robot name
    name: str
    # which joint belong to each arm
    chains: dict = field(default_factory=dict)
    # limits for joint
    limits: dict = field(default_factory=dict)
    end_effectors: dict = field(default_factory=dict)
    grippers: dict = field(default_factory=dict)  

    def get_chain(self, name: str) -> List[str]:
        return self.chains.get(name, [])

    def get_end_effector(self, name: str) -> Tuple[str, str]:
        return self.end_effectors[name]

    # keep a joint inside its limits
    def clamp_joint(self, joint_name: str, value: float) -> float:
        if joint_name in self.limits:
            lo, hi = self.limits[joint_name]
            return max(lo, min(hi, value))
        return value

    def get_gripper(self, side: str) -> dict:
        return self.grippers.get(side, {})
