from motion_pipeline.core.schema import Program


class BasicRMLEmitter:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent

    def emit(self, program: Program) -> str:
        lines = [f"define {program.name}"]
        for move in program.moves:
            lines.append(f"{self.indent}move {move.side} {move.joint} {move.rotation} to {move.position}")
        lines.append("end")
        return "\n".join(lines)

