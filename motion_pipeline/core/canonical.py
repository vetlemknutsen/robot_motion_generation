from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class JointAngle:
    """Description of a single joint component in degrees."""

    joint: str
    component: str
    degrees: float
    side: Optional[str] = None


@dataclass
class CanonicalFrame:
    """Snapshot of the canonical body pose at a specific timestamp."""

    time: float
    joint_angles: List[JointAngle] = field(default_factory=list)


@dataclass
class CanonicalMotion:
    """Time-based canonical motion representation independent of any robot."""

    name: str
    frames: List[CanonicalFrame] = field(default_factory=list)
