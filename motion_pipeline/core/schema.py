from dataclasses import dataclass, field
from typing import List


@dataclass
class Move:
    joint: str          
    position: float    


@dataclass
class Program:
    name: str
    moves: List[Move] = field(default_factory=list)
