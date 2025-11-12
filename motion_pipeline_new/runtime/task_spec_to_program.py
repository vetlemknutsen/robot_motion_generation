from typing import List

from motion_pipeline.core.schema import Move, MultiMove, Program, Repeat, Stage
from motion_pipeline.core.task_spec import MotionDirective, StageDefinition


def task_spec_to_program(spec: MotionDirective) -> Program:
    stages: List[Stage] = []

    for stage_spec in spec.stages:
        instructions = []
        for entry in stage_spec.instructions:
            entry_type = entry.get("type", "move")

            if entry_type == "move":
                instructions.append(_entry_to_move(entry))

            elif entry_type == "multi":
                moves = [_entry_to_move(m) for m in entry.get("moves", [])]
                if moves:
                    instructions.append(MultiMove(moves=moves))

            elif entry_type == "repeat":
                inner = []
                for inner_entry in entry.get("instructions", []):
                    inner_type = inner_entry.get("type", "move")
                    if inner_type == "multi":
                        inner_moves = [_entry_to_move(m) for m in inner_entry.get("moves", [])]
                        if inner_moves:
                            inner.append(MultiMove(moves=inner_moves))
                    else:
                        inner.append(_entry_to_move(inner_entry))

                if inner:
                    instructions.append(Repeat(count=int(entry["count"]), instructions=inner))

            else:
                raise ValueError(f"Unknown stage entry type: {entry_type}")

        if instructions:
            stages.append(Stage(name=stage_spec.name, instructions=instructions))

    if not stages:
        raise ValueError("Task specification did not produce any stages.")
    


    return Program(name=spec.name, stages=stages)


def _entry_to_move(entry: dict) -> Move:
    side = entry.get("side")
    return Move(
        side=side.lower() if side else None,
        joint=entry["joint"].lower(),
        rotation=entry["rotation"].lower(),
        position=float(entry["position"]),
    )
