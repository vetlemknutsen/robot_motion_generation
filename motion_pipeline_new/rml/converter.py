from motion_pipeline.core.schema import Move, MultiMove, Program, Repeat


def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for stage in program.stages:
        for instr in stage.instructions:
            commands.append(_instruction_to_legacy(instr))
    return {"def": program.name, "commands": commands}

def _instruction_to_legacy(instr):
    if isinstance(instr, Move):
        payload = {"joint": instr.joint, "rotation": instr.rotation, "position": float(instr.position)}
        if instr.side:
            payload["side"] = instr.side
        return {"move": payload}

    if isinstance(instr, MultiMove):
        return {"multimove": [ {"move": _instruction_to_legacy(move)["move"]} for move in instr.moves ]}

    if isinstance(instr, Repeat):
        return {
            "repeat": [_instruction_to_legacy(inner) for inner in instr.instructions],
            "amount": instr.count,
        }

    raise TypeError(f"Unknown instruction type: {instr}")
