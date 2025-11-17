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

ProgramInstruction = Union[Move, MultiMove]

@dataclass
class Program:
    name: str
    instructions: List[ProgramInstruction] = field(default_factory=list)
