from typing import List, Tuple
from motion_pipeline.core.task_spec import MotionDirective
from motion_pipeline.core.schema import Move, Program

# Convert directive to Program format
def directive_to_program(directive: MotionDirective) -> Tuple[Program, List[Tuple[int, str]]]:
    moves=[]
    markers=[]
    idx = 0

    for stage in directive.stages:
        markers.append((idx, stage.name))
        for raw in stage.moves:
            moves.append(Move(
                side=(raw.get("side") or "").lower() or None,
                joint=raw["joint"].lower(),
                rotation=raw["rotation"].lower(),
                position=float(raw["position"]),
            ))
            idx += 1

    return Program(name=directive.name or "unnamed", moves=moves), markers
