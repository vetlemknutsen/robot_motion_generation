from motion_pipeline.rml.base import Emitter
from motion_pipeline.core.joint_level import Move, MultiMove, Program
from motion_pipeline.runtime.configs.robot_config import RobotConfig

# Emitter that writes Program into RML
class BasicRMLEmitter(Emitter):
    def __init__(self, config: RobotConfig) -> None:
        self.tab = "   "
        self.joint_map = config.joint_map  

    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]

        for instr in program.instructions:
            if isinstance(instr, Move):
                line = self._emit_move(instr)
                if line:
                    lines.append(line)
            else:
                lines.extend(self._emit_multimove(instr))
        lines.append("end")
        return "\n".join(lines)

    def _emit_move(self, move: Move) -> str:
        joint = move.joint
        if joint not in self.joint_map:
            return None  
        side, group, rotation = self.joint_map[joint]
        return f"{self.tab}move {side} {group} {rotation} to {move.position}"

    def _emit_multimove(self, block: MultiMove) -> list[str]:
        move_lines = []
        for move in block.moves:
            line = self._emit_move(move)
            if line:
                move_lines.append(f"{self.tab}{line}")
        if not move_lines:
            return []
        return [f"{self.tab}multimove"] + move_lines + [f"{self.tab}end"]
