from typing import List, Tuple
from motion_pipeline.core.joint_level import Move, MultiMove, Program

# Emitter that writes Program into RML
class BasicRMLEmitter:
    def __init__(self) -> None:
        self.tab = "   "
    
    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]

        for i, instr in enumerate(program.instructions):
            if isinstance(instr, Move):
                lines.append(self._emit_move(instr))
            else:
                lines.extend(self._emit_multimove(instr))
        lines.append("end")
        return "\n".join(lines)

    def _emit_move(self, move: Move) -> str:
        parts = ["move"]
        if move.side: 
            parts.append(move.side)
        parts.extend([move.joint,move.rotation, "to", str(move.position)])
        return f"{self.tab}{' '.join(parts)}"
    
    def _emit_multimove(self, block: MultiMove) -> list[str]:
        lines = [f"{self.tab}multimove"]
        for move in block.moves: 
            lines.append(f"{self.tab}{self._emit_move(move)}")
        lines.append(f"{self.tab}end")
        return lines
    