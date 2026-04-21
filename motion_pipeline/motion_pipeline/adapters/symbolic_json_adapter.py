import json
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_level import Frame, TaskDescription, Target, GripperState


class JsonScenarioAdapter(Adapter):
    def to_taskdescription(self, source) -> TaskDescription:
        with Path(source).open() as f:
            data = json.load(f)

        motion_name = data.get("name", Path(source).stem)
        frames_data = data.get("frames", [])

        frames = []
        for i, frame_data in enumerate(frames_data):
            frame = self._parse_frame(i, frame_data)
            frames.append(frame)

        return TaskDescription(motion_name, frames)

    def _parse_frame(self, time, frame_data):
        action = frame_data.get("action")
        side = frame_data.get("side", "right")

        targets = []
        grippers = []

        if action == "move":
            position = frame_data["position"]
            orientation = frame_data.get("orientation")
            if orientation:
                orientation = [float(v) for v in orientation] 
            targets.append(Target(side=side, position=position, orientation=orientation))

        elif action == "gripper":
            state = frame_data.get("state", "open")
            grippers.append(GripperState(side=side, closed=(state == "closed")))

        else:
            raise ValueError(f"Unknown action: {action}")

        return Frame(time=float(time), targets=targets, grippers=grippers)
