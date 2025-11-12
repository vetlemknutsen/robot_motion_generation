from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class SceneObject:
    object_id: str
    pose: Optional[Tuple[float, float, float, float, float, float, float]] = None


@dataclass
class StageDefinition:
    name: str
    description: Optional[str] = None
    instructions: List[dict] = field(default_factory=list)


@dataclass
class MotionDirective:
    name: str
    source: Optional[str]
    destination: Optional[str]
    objects: List[SceneObject] = field(default_factory=list)
    stages: List[StageDefinition] = field(default_factory=list)
