from typing import List, Tuple
from motion_pipeline.core.schema import Program


class BasicRMLEmitter:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent
    
    def emit_with_stages(self, program: Program, stage_markers: List[Tuple[int, str]]) -> str:
        marker_map = {index: name for index, name in stage_markers}
        lines = [f"define {program.name}"]
        for idx, move in enumerate(program.moves):
            if idx in marker_map:
                lines.append(f"{self.indent}// stage: {marker_map[idx]}")
            parts = ["move"]
            if move.side:
                parts.append(move.side)
            parts.extend([move.joint, move.rotation, "to", str(move.position)])
            lines.append(f"{self.indent}{' '.join(parts)}")
        lines.append("end")
        return "\n".join(lines)
    