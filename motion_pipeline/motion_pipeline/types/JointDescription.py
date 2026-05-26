from dataclasses import dataclass, field
from typing import List, Optional, Union


# A single joint movement: which side (left/right), which joint, 
# rotation type, and how far to rotate
@dataclass
class Move:
    side: Optional[str] 
    joint: str 
    rotation: str         
    position: float  


# Several Moves grouped together so they happen at the same time
@dataclass 
class MultiMove: 
    moves: List[Move]

JointCommand = Union[Move, MultiMove]


# A whole motion described in joint-space (after IK has run)
@dataclass
class JointDescription:
    name: str
    commands: List[JointCommand] = field(default_factory=list)
