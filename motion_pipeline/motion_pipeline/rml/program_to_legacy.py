from motion_pipeline.core.joint_level import Move, MultiMove, Program


def _parse_joint_name(name: str) -> tuple:
    """
    Parse joint name into (side, joint, rotation) components.
    E.g., 'RShoulderPitch' -> ('R', 'Shoulder', 'Pitch')
          'LElbowRoll' -> ('L', 'Elbow', 'Roll')
          'HeadYaw' -> ('', 'Head', 'Yaw')
          'arm_1_joint' -> ('', 'arm_1_joint', '')  # unchanged for TIAGo-style names
    """
    # Check for side prefix (R or L followed by uppercase)
    side = ''
    if name and name[0] in ('R', 'L') and len(name) > 1 and name[1].isupper():
        side = name[0]
        name = name[1:]

    # Find rotation suffix (Roll, Pitch, Yaw)
    rotation = ''
    for rot in ('Roll', 'Pitch', 'Yaw'):
        if name.endswith(rot):
            rotation = rot
            name = name[:-len(rot)]
            break

    return side, name, rotation


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
    # If rotation is empty and joint looks like a full NAO-style name, parse it
    if not move.rotation and move.joint and len(move.joint) > 1:
        side, joint, rotation = _parse_joint_name(move.joint)
        # Only use parsed values if parsing found something meaningful
        if rotation:
            entry = {
                "joint": joint,
                "rotation": rotation,
                "position": float(move.position),
            }
            if side:
                entry["side"] = side
            return entry

    # Default: use values as-is
    entry = {
        "joint": move.joint,
        "rotation": move.rotation,
        "position": float(move.position),
    }
    if move.side:
        entry["side"] = move.side
    return entry

