from dataclasses import dataclass, field
from typing import List, Optional

# Information for a specific joint
@dataclass
class JointAngle:
    joint: str
    component: str
    degrees: float
    side: Optional[str] = None

@dataclass
class EndEffectorTarget:
    side: str
    position: List[float] 
    orientation: Optional[List[float]] = None  


# A list of JointAngle's for a frame
@dataclass
class PoseFrame:
    time: float
    joint_angles: List[JointAngle] = field(default_factory=list)
    targets: List[EndEffectorTarget] = field(default_factory=list)


# List of frames = Motion
@dataclass
class MotionSequence:
    name: str
    frames: List[PoseFrame] = field(default_factory=list)
