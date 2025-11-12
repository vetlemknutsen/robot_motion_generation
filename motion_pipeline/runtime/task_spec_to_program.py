from typing import List, Tuple
from motion_pipeline.core.task_spec import MotionDirective
from motion_pipeline.core.schema import Move, MultiMove, Program

# Convert directive to Program format
def directive_to_program(directive: MotionDirective) -> Tuple[Program, List[Tuple[int, str]]]:
    instructions = []
    

    for stage in directive.stages:
        for raw in stage.moves:
            instructions.append(_entry_to_instruction(raw))
           
    return Program(name=directive.name, instructions=instructions)


def _entry_to_instruction(entry: dict):
    if entry.get("type") == "multimove":
        moves = [_dict_to_move(move_dict) for move_dict in entry.get("moves", [])]
        return MultiMove(moves=moves)
    return _dict_to_move(entry)

def _dict_to_move(entry: dict) -> Move: 
    return Move(
        side=(entry.get("side")),
        joint=entry["joint"],
        rotation=entry["rotation"],
        position=float(entry["position"])
    )