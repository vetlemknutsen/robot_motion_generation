from motion_pipeline.rml.base import Emitter
from motion_pipeline.types.JointDescription import Move, MultiMove, JointDescription
from motion_pipeline.pipeline.configs.robot_config import RobotConfig

# Turns a JointDescription (joint-space program) into RML
class BasicRMLEmitter(Emitter):
    def __init__(self, config: RobotConfig) -> None:
        self.tab = "   " #indentation used in the output
        self.joint_map = config.joint_map  # maps raw joint names -> (side, group, rotation)

    def emit(self, program: JointDescription) -> str:
        # top-level wrapper: define <name>
        lines = [f"define {program.name}"]

        for instr in program.instructions:
            # single move -> one line, multimove -> block of lines
            if isinstance(instr, Move):
                line = self._emit_move(instr)
                if line:
                    lines.append(line)
            else:
                lines.extend(self._emit_multimove(instr))
        lines.append("end")
        return "\n".join(lines)

    # Make one "move ..." RML line from a Move
    # Returns None if we dont have a mapping for this joint (we skip it)
    def _emit_move(self, move: Move) -> str:
        joint = move.joint
        if joint not in self.joint_map:
            return None  
        side, group, rotation = self.joint_map[joint]
        return f"{self.tab}move {side} {group} {rotation} to {move.position}"

    # Emit a "multimove ... end" block. All moves inside happen together. 
    def _emit_multimove(self, block: MultiMove) -> list[str]:
        move_lines = []
        for move in block.moves:
            line = self._emit_move(move)
            if line:
                # extra tab so it nests nicely under "multimove"
                move_lines.append(f"{self.tab}{line}")
        # if no moves, skip block entirely
        if not move_lines:
            return []
        return [f"{self.tab}multimove"] + move_lines + [f"{self.tab}end"]
