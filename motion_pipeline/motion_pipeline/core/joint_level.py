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

JointInstruction = Union[Move, MultiMove]

@dataclass
class JointDescription:
    name: str
    instructions: List[JointInstruction] = field(default_factory=list)
