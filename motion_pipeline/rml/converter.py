from motion_pipeline.core.schema import Move, MultiMove, Program

# Convert to old JSON format so Webots helpers still work
def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for move in _flatten_instructions(program.instructions):
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

def _flatten_instructions(instructions: list) -> list[Move]:
    flat = []
    for instr in instructions:
        if isinstance(instr, MultiMove):
            flat.extend(instr.moves)
        else: 
            flat.append(instr)
    return flat

