import json
from pathlib import Path
from typing import Any, Mapping

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_spec import MotionDirective, SceneObject, StageDefinition


class JsonAdapter(Adapter):
    def can_handle(self, source: Any) -> bool:
        if isinstance(source, (str, Path)):
            return str(source).endswith(".json")
        if isinstance(source, Mapping):
            return "task" in source  
        return False

    def to_directive(self, source: Any) -> MotionDirective:
        data = self._load_data(source)

        objects = [
            SceneObject(obj["id"], tuple(obj["pose"]) if "pose" in obj else None)
            for obj in data.get("objects", [])
        ]

        stages = []
        for raw_stage in data.get("stages", []):
            moves = raw_stage.get("moves", [])
            stages.append(StageDefinition(
                name=raw_stage.get("name", "stage"),
                moves=moves,
            ))

        primitive_moves = data.get("moves", [])
        for stage in stages:
            primitive_moves.extend(stage.moves)

        return MotionDirective(
            name=data.get("task", "unnamed"),
            source=data.get("source"),
            destination=data.get("destination"),
            objects=objects,
            stages=stages,
        )

    def _load_data(self, source: Any) -> Mapping[str, Any]:
        if isinstance(source, (str, Path)):
            with open(source) as f:
                return json.load(f)
        return source  
