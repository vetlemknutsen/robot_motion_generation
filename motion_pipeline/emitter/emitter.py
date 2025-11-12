from typing import List, Tuple
from motion_pipeline.core.schema import Program

# Emitter that writes Program into RML
class BasicRMLEmitter:
    def __init__(self) -> None:
        self.tab = "   "
    
    def emit(self, program: Program) -> str:
        lines=[f"define {program.name}"]
        for move in program.moves: 
            parts = ["move"]
            if move.side:
                parts.append(move.side)
            parts.extend([move.joint, move.rotation, "to", str(move.position)])
            lines.append(self.tab + " ".join(parts))
        lines.append("end")
        return "\n".join(lines)

    