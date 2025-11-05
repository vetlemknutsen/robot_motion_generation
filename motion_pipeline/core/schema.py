from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Move:
    side: Optional[str] 
    joint: str 
    rotation: str         
    position: float    


@dataclass
class Program:
    name: str
    moves: List[Move] = field(default_factory=list)
