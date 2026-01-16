from dataclasses import dataclass, field
from typing import List, Optional



@dataclass
class Target:
    side: str
    position: List[float]
    orientation: Optional[List[float]] = None


@dataclass
class GripperState:
    side: str
    closed: bool  


# A list of JointAngle's for a frame
@dataclass
class Frame:
    time: float # unused
    targets: List[Target] = field(default_factory=list)
    grippers: List[GripperState] = field(default_factory=list)


# List of frames = Motion
@dataclass
class Motion:
    name: str
    frames: List[Frame] = field(default_factory=list)
