from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class StageDefinition:
    name: str
    moves: List[dict] = field(default_factory=list)


@dataclass
class MotionDirective:
    name: str
    stages: List[StageDefinition] = field(default_factory=list)