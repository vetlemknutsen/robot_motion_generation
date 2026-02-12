from motion_pipeline.core.joint_level import Move, MultiMove, Program
from motion_pipeline.runtime.configs.robot_config import RobotConfig

# Emitter that writes Program into RML
class BasicRMLEmitter:
    def __init__(self, config: RobotConfig) -> None:
        self.tab = "   "
        self.joint_map = config.joint_map  

    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]

        for instr in program.instructions:
            if isinstance(instr, Move):
                lines.append(self._emit_move(instr))
            else:
                lines.extend(self._emit_multimove(instr))
        lines.append("end")
        return "\n".join(lines)

    def _emit_move(self, move: Move) -> str:
        joint = move.joint
        if joint not in self.joint_map:
            raise ValueError(f"Joint '{joint}' not found in joint_map. Add it to joint_groups in the robot config.")
        side, group, rotation = self.joint_map[joint]
        return f"{self.tab}move {side} {group} {rotation} to {move.position}"

    def _emit_multimove(self, block: MultiMove) -> list[str]:
        lines = [f"{self.tab}multimove"]
        for move in block.moves:
            lines.append(f"{self.tab}{self._emit_move(move)}")
        lines.append(f"{self.tab}end")
        return lines
