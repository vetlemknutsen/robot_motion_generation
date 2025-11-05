from motion_pipeline.core.schema import Move, Program


def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for move in program.moves:
        entry = {
            "joint": move.joint,          
            "rotation": move.rotation,     
            "position": float(move.position),
        }
        if move.side:
            entry["side"] = move.side    

        commands.append({"move": entry})

    return {
        "def": program.name,
        "commands": commands,
    }
