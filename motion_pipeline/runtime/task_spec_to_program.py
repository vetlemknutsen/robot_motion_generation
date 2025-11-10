from typing import List, Tuple
from motion_pipeline.core.task_spec import MotionDirective
from motion_pipeline.core.schema import Move, Program

def directive_to_program(directive: MotionDirective) -> Tuple[Program, List[Tuple[int, str]]]:
    moves = []
    stage_markers = []
    index = 0

    if directive.stages:
        for stage in directive.stages:
            if stage.moves:
                stage_markers.append((index, stage.name))
                for entry in stage.moves:
                    moves.append(_entry_to_move(entry))
                    index += 1
    else:
        for entry in directive.primitive_moves:
            moves.append(_entry_to_move(entry))
            index += 1

    program = Program(name=directive.name, moves=moves)
    return program, stage_markers

def _entry_to_move(entry: dict) -> Move:
    side = entry.get("side")
    return Move(
        side=side.lower() if side else None,
        joint=entry["joint"].lower(),
        rotation=entry["rotation"].lower(),
        position=float(entry["position"]),
    )
