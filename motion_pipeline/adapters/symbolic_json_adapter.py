import json
from pathlib import Path
from typing import Dict, List

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.motion import PoseFrame, MotionSequence, EndEffectorTarget, GripperState


class JsonScenarioAdapter(Adapter):
    def __init__(self):
        self.last_positions: Dict[str, List[float]] = {}
    
    def to_motion(self, source) -> MotionSequence:
        with Path(source).open() as f:
            data = json.load(f)
        
        motion_name = data.get("name", Path(source).stem)
        frames_data = data.get("frames", [])
        
        self.last_positions = {}
 
        frames = []
        for i, frame_data in enumerate(frames_data):
            frame = self._parse_frame(i, frame_data)
            frames.append(frame)
        
        return MotionSequence(motion_name, frames)
    
    def _parse_frame(self, time: int, frame_data: dict) -> PoseFrame:
        action = frame_data.get("action")
        side = frame_data.get("side", "right")

        targets = []
        grippers = []

        if action == "reach":
            position = frame_data["position"]
            self.last_positions[side] = position
            targets.append(EndEffectorTarget(side=side, position=position))
            grippers.append(GripperState(side=side, closed=False))

        elif action == "grasp":
            if side not in self.last_positions:
                raise ValueError(f"Cannot grasp without first reaching (side: {side})")
            position = self.last_positions[side]
            targets.append(EndEffectorTarget(side=side, position=position))
            grippers.append(GripperState(side=side, closed=True))

        elif action == "move":
            position = frame_data["position"]
            self.last_positions[side] = position
            targets.append(EndEffectorTarget(side=side, position=position))

        elif action == "release":
            if side not in self.last_positions:
                raise ValueError(f"Cannot release without first reaching (side: {side})")
            position = self.last_positions[side]
            targets.append(EndEffectorTarget(side=side, position=position))
            grippers.append(GripperState(side=side, closed=False))

        else:
            raise ValueError(f"Unknown action: {action}")

        return PoseFrame(
            time=float(time),
            joint_angles=[],
            targets=targets,
            grippers=grippers
        )
