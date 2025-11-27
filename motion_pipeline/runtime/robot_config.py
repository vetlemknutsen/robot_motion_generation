from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class RobotConfig:
    name: str
    urdf_path: Path
    chains: Dict[str, List[str]] = field(default_factory=dict)
    limits: Dict[str, tuple[float, float]] = field(default_factory=dict)

    def get_chain(self, name: str) -> List[str]:
        return self.chains.get(name, [])

    def clamp_joint(self, joint_name: str, value: float) -> float:
        if joint_name in self.limits:
            a, b = self.limits[joint_name]
            return max(a, min(b, value))
        return value
