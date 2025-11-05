from typing import Any, Dict, List

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.schema import Move, Program


class DemoAdapter(Adapter):
    def to_program(self, source: Dict[str, Any]) -> Program:
        moves_data: List[Dict[str, Any]] = source.get("moves", [])
        moves = [
            Move(
                side=move["side"],
                joint=move["joint"],
                rotation=move["rotation"],
                position=float(move["position"]),
            )
            for move in moves_data
        ]
        return Program(name=source.get("name", "demo_motion"), moves=moves)
