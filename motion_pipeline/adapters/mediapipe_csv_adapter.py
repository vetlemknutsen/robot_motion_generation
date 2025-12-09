import csv
import math
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.motion import PoseFrame, MotionSequence, EndEffectorTarget, GripperState


class MediaPipeCSVAdapter(Adapter):
    def to_motion(self, source) -> MotionSequence:
        path = Path(source)
        frames = []

        with path.open() as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                frame = self._parse_row(i, row)
                frames.append(frame)

        return MotionSequence(path.stem, frames)

    def _parse_row(self, frame_num, row):
        targets = []
        grippers = []

        if "RIGHT_WRIST_x" in row:
            # X=right, Y=down, Z=toward camera
            wrist_x = float(row["RIGHT_WRIST_x"])
            wrist_y = float(row["RIGHT_WRIST_y"])
            wrist_z = float(row["RIGHT_WRIST_z"])

            # X=forward, Y=left, Z=up
            robot_x = wrist_z + 0.5
            robot_y = -wrist_x     
            robot_z = -wrist_y + 0.5

            # TIAGo reachable workspace
            robot_x = max(0.25, min(0.7, robot_x))
            robot_y = max(-0.5, min(0.5, robot_y))
            robot_z = max(0.4, min(1.1, robot_z))

            targets.append(EndEffectorTarget(
                side="right",
                position=[round(robot_x, 3), round(robot_y, 3), round(robot_z, 3)]
            ))

            grip = self._detect_pinch(row)
            if grip is not None:
                grippers.append(GripperState(side="right", closed=grip))

        return PoseFrame(time=float(frame_num), targets=targets, grippers=grippers)

    def _detect_pinch(self, row):
        if "RIGHT_THUMB_TIP_x" not in row or "RIGHT_INDEX_FINGER_TIP_x" not in row:
            return None

        # thumb and index finger positions
        thumb_x = float(row["RIGHT_THUMB_TIP_x"])
        thumb_y = float(row["RIGHT_THUMB_TIP_y"])
        thumb_z = float(row["RIGHT_THUMB_TIP_z"])

        index_x = float(row["RIGHT_INDEX_FINGER_TIP_x"])
        index_y = float(row["RIGHT_INDEX_FINGER_TIP_y"])
        index_z = float(row["RIGHT_INDEX_FINGER_TIP_z"])

        # euclidean distance
        dist = math.sqrt(
            (thumb_x - index_x) ** 2 +
            (thumb_y - index_y) ** 2 +
            (thumb_z - index_z) ** 2
        )
        
        return dist < 0.05
