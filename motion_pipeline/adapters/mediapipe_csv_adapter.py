import csv
import math
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_level import Frame, Motion, Target, GripperState
from motion_pipeline.runtime.configs.robot_config import RobotConfig


class MediaPipeCSVAdapter(Adapter):
    def __init__(self, config: RobotConfig):
        self.config = config

    def to_motion(self, source) -> Motion:
        path = Path(source)
        frames = []

        with path.open() as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                frame = self._parse_row(i, row)
                frames.append(frame)

        return Motion(path.stem, frames)

    def _parse_row(self, frame_num, row):
        targets = []
        grippers = []

        if "RIGHT_WRIST_x" in row:
            # X=right, Y=down, Z=toward camera
            wrist_x = float(row["RIGHT_WRIST_x"])
            wrist_y = float(row["RIGHT_WRIST_y"])
            wrist_z = float(row["RIGHT_WRIST_z"])

            # X=forward, Y=left, Z=up
            robot_x = wrist_z + 0.2
            robot_y = -wrist_x - 0.2
            robot_z = -wrist_y + 0.4

            robot_x = self.config.clamp_position("x", robot_x)
            robot_y = self.config.clamp_position("y", robot_y)
            robot_z = self.config.clamp_position("z", robot_z)

            targets.append(Target(
                side="right",
                position=[round(robot_x, 3), round(robot_y, 3), round(robot_z, 3)]
            ))

            grip = self._detect_pinch(row)
            if grip is not None:
                grippers.append(GripperState(side="right", closed=grip))

        return Frame(time=float(frame_num), targets=targets, grippers=grippers)

    def _detect_pinch(self, row):
        required_fields = [
            "RIGHT_THUMB_TIP_x",
            "RIGHT_THUMB_TIP_y",
            "RIGHT_THUMB_TIP_z",
            "RIGHT_INDEX_FINGER_TIP_x",
            "RIGHT_INDEX_FINGER_TIP_y",
            "RIGHT_INDEX_FINGER_TIP_z",
        ]

        if not row:
            return True 

        try:
            values = {field: row[field] for field in required_fields}
        except KeyError:
            return True  

        if any(v is None or str(v).strip() == "" for v in values.values()):
            return True  

        # thumb and index finger positions
        thumb_x = float(values["RIGHT_THUMB_TIP_x"])
        thumb_y = float(values["RIGHT_THUMB_TIP_y"])
        thumb_z = float(values["RIGHT_THUMB_TIP_z"])

        index_x = float(values["RIGHT_INDEX_FINGER_TIP_x"])
        index_y = float(values["RIGHT_INDEX_FINGER_TIP_y"])
        index_z = float(values["RIGHT_INDEX_FINGER_TIP_z"])

        # euclidean distance
        dist = math.sqrt(
            (thumb_x - index_x) ** 2 +
            (thumb_y - index_y) ** 2 +
            (thumb_z - index_z) ** 2
        )

        return dist < 0.051
