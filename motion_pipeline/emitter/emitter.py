from motion_pipeline.core.schema import Program


class BasicRMLEmitter:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent

    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]
        for move in program.moves:
            parts = ["move"]
            if move.side:
                parts.append(move.side)
            parts.extend([move.joint, move.rotation, "to", str(move.position)])
            lines.append(f"{self.indent}{' '.join(parts)}")
        lines.append("end")
        return "\n".join(lines)

