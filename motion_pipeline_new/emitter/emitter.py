from typing import List, Tuple
from motion_pipeline.core.schema import Move, MultiMove, Program, Repeat


class BasicRMLEmitter:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent


    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]
        for stage in program.stages:
            lines.append(f"{self.indent}// stage: {stage.name}")
            for instr in stage.instructions:
                lines.extend(self._emit_instruction(instr, indent_level=1))
        lines.append("end")
        return "\n".join(lines)

    def _emit_instruction(self, instr, indent_level: int) -> list[str]:
        indent = self.indent * indent_level
        if isinstance(instr, Move):
            parts = ["move"]
            if instr.side:
                parts.append(instr.side)
            parts.extend([instr.joint, instr.rotation, "to", f"{instr.position:g}"])
            return [f"{indent}{' '.join(parts)}"]

        if isinstance(instr, MultiMove):
            lines = [f"{indent}multimove"]
            for move in instr.moves:
                lines.extend(self._emit_instruction(move, indent_level + 1))
            lines.append(f"{indent}end")
            return lines

        if isinstance(instr, Repeat):
            lines = [f"{indent}repeat {instr.count}"]
            for inner in instr.instructions:
                lines.extend(self._emit_instruction(inner, indent_level + 1))
            lines.append(f"{indent}end")
            return lines

        raise TypeError(f"Unknown instruction type: {instr}")
