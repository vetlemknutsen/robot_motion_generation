from motion_pipeline.core.schema import Move, Program


def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for move in program.moves:
        commands.append({
            "move": {
                "joint": move.joint,
                "position": float(move.position),
            }
        })
    return {
        "def": program.name,
        "commands": commands,
    }
