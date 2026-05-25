import json
from pathlib import Path

from motion_pipeline.adapters.base import Adapter, register_adapter
from motion_pipeline.types.TaskDescription import Frame, TaskDescription, Target, GripperState

@register_adapter("json")
class SimpleJSONAdapter(Adapter):
    # Reads a JSON file with a list of frames and turns it into a TaskDescription
    def to_taskdescription(self, source) -> TaskDescription:
        with Path(source).open() as f:
            data = json.load(f)

        # use the name field if it exists, else filename
        motion_name = data.get("name", Path(source).stem)
        frames_data = data.get("frames", [])

        frames = []
        for i, frame_data in enumerate(frames_data):
            frame = self._parse_frame(i, frame_data)
            frames.append(frame)

        return TaskDescription(motion_name, frames)

    # Turn one JSON frame into a Frame object
    # Two kinds of actions: "reach" or "gripper"
    def _parse_frame(self, time, frame_data):
        action = frame_data.get("action")
        side = frame_data.get("side", "right") # default to right side

        targets = []
        grippers = []

        if action == "reach":
            position = frame_data["position"]
            orientation = frame_data.get("orientation")
            # make sure orientation values are floats
            if orientation:
                orientation = [float(v) for v in orientation] 
            targets.append(Target(side=side, position=position, orientation=orientation))

        elif action == "gripper":
            state = frame_data.get("state", "open")
            # store as boolean: True = closed, False = open
            grippers.append(GripperState(side=side, closed=(state == "closed")))

        else:
            raise ValueError(f"Unknown action: {action}")

        return Frame(time=float(time), targets=targets, grippers=grippers)
