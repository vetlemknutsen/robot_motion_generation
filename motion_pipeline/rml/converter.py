from motion_pipeline.core.schema import Move, MultiMove, Program

# Convert to old JSON format so Webots helpers still work
def program_to_legacy_payload(program: Program) -> dict:
    commands = []
    for instr in program.instructions:
        if isinstance(instr, MultiMove):
            commands.append({
                "multimove" : [{"move": _move_entry(move)} for move in instr.moves]
            })
        else: 
            commands.append({"move": _move_entry(instr)})
            
    return {
        "def": program.name,
        "commands": commands,
    }

def _move_entry(move: Move) -> dict: 
    entry = {
        "joint": move.joint, 
        "rotation": move.rotation, 
        "position": float(move.position),
    }
    if move.side: 
        entry["side"] = move.side
    return entry

