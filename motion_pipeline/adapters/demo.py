from typing import Any, Dict, List

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.schema import Move, Program


class DemoAdapter(Adapter):
    def to_program(self, source: Dict[str, Any]) -> Program:
        moves = []
        for entry in source.get("moves", []):
            side = entry.get("side")
            moves.append(
                Move(
                    side=side.lower() if side else None,
                    joint=entry["joint"].lower(),
                    rotation=entry["rotation"].lower(),
                    position=float(entry["position"]),
                )
            )
        return Program(name=source.get("name", "demo_motion"), moves=moves)
