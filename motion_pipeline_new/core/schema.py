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

@dataclass 
class Repeat:
    count: int
    instructions: List[Union[Move, MultiMove]]  

StageInstruction = Union[Move, MultiMove, Repeat]

@dataclass 
class Stage:
    name: str 
    instructions: List[StageInstruction]


@dataclass
class Program:
    name: str
    stages: List[Stage] = field(default_factory=list)
