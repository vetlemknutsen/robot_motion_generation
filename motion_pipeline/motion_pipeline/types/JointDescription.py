from dataclasses import dataclass, field
from typing import List, Optional, Union

@dataclass
class Move:
    side: Optional[str] 
    joint: str 
    rotation: str         
    position: float  

@dataclass 
class MultiMove: 
    moves: List[Move]

JointCommand = Union[Move, MultiMove]

@dataclass
class JointDescription:
    name: str
    instructions: List[JointCommand] = field(default_factory=list)
