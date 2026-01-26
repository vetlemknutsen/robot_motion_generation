from typing import List, Tuple
from motion_pipeline.core.joint_level import Move, MultiMove, Program
from motion_pipeline.rml.program_to_legacy import _parse_joint_name

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
        side = move.side
        joint = move.joint
        rotation = move.rotation

        # If NAO
        if not rotation and joint and joint[0] in ("R", "L") and len(joint) > 1 and joint[1].isupper():
            s, j, r = _parse_joint_name(joint)
            if r:
                if not side:
                    side = "right" if s == "R" else "left" if s == "L" else ""
                joint = j.lower()
                rotation = r.lower()

        parts = ["move"]
        if side:
            parts.append(side)
        for p in (joint, rotation, "to", str(move.position)):
            if p:
                parts.append(p)
        return f"{self.tab}{' '.join(parts)}"

    
    def _emit_multimove(self, block: MultiMove) -> list[str]:
        lines = [f"{self.tab}multimove"]
        for move in block.moves: 
            lines.append(f"{self.tab}{self._emit_move(move)}")
        lines.append(f"{self.tab}end")
        return lines
    