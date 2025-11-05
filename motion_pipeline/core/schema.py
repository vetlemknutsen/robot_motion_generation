from dataclasses import dataclass, field
from typing import List


@dataclass
class Move:
    side: str 
    joint: str 
    rotation: str         
    position: float    


@dataclass
class Program:
    name: str
    moves: List[Move] = field(default_factory=list)
