import json
from pathlib import Path
from typing import Any, Mapping

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_spec import MotionDirective, StageDefinition

# Adapter for JSON files
class JsonAdapter(Adapter):

    def to_directive(self, source: Any) -> MotionDirective:
        data = self._load(source)
        stages = self._collect_stages(data)
        
        return MotionDirective(
            name=data.get("name"),
            stages=stages
        )
    
    # collect all stages in input
    def _collect_stages(self, data: Mapping[str, Any]) -> list[StageDefinition]:
        stages = []
        stages.append(StageDefinition(
            name=data.get("name", "main"),
            moves=data["moves"],))

        return stages

    # load json input
    def _load(self, source: Any) -> Mapping[str, Any]:
        if isinstance(source, (str, Path)):
            with open(source) as f:
                return json.load(f)
        return source  
