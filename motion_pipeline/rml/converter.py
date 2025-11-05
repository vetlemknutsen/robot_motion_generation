from motion_pipeline.core.schema import Move, Program


def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for move in program.moves:
        joint_name = f"{move.side[0].upper()}{move.joint.capitalize()}{move.rotation.capitalize()}"
        commands.append({
            "move": {
                "joint": joint_name,
                "position": float(move.position),
            }
        })
    return {
        "def": program.name,
        "commands": commands,
    }
