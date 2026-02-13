from dataclasses import dataclass, field
from typing import List, Optional


# Datatypes for the task-evel motion representation
@dataclass
class Target:
    """
    End-effector target in task-space
    side: "right" or "left"
    position: [x, y, z] in meters relative to robot base frame
    orientation: optional orientation of end-effector [x, y, z, w]
    """
    side: str
    position: List[float]
    orientation: Optional[List[float]] = None


@dataclass
class GripperState:
    """
    Gripper, which side and whether to close or open.
    side: "right" or "left"
    closed: True or False
    """
    side: str
    closed: bool  


@dataclass
class Frame:
    """
    One step with the end-effector targets and gripper states to reach.
    time: currently unused, may be used for timing
    targets: end-effector targets
    grippers: gripper states at each step
    """
    time: float # unused for now
    targets: List[Target] = field(default_factory=list)
    grippers: List[GripperState] = field(default_factory=list)


@dataclass
class Motion:
    """
    Multiple steps/frames. This is what adapters produce, it's
    robot-independent and describes motion in task-space. The IK solver
    then converts it to joint-space commands.
    """
    name: str
    frames: List[Frame] = field(default_factory=list)
