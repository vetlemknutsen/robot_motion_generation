import csv
import math
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_level import Frame, TaskDescription, Target, GripperState

SIDE = "right"
PINCH_THRESHOLD = 0.05


class MediaPipeCSVAdapter(Adapter):

    def to_taskdescription(self, source) -> TaskDescription:
        path = Path(source)
        with path.open() as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return TaskDescription(path.stem, [])

        ax, ay, _ = self._avg_ankle(rows[0])
        frames = []
        prev_grip = None
        p = SIDE.upper()

        for i, row in enumerate(rows):
            # only generate frames when grip changes (grab/release)
            grip = self._pinch(row)
            if grip == prev_grip:
                continue
            prev_grip = grip

            try:
                wx = float(row[f"{p}_WRIST_x"])
                wy = float(row[f"{p}_WRIST_y"])
            except (KeyError, ValueError):
                continue

            pos = [0.5, round(wx - ax, 3), round(-(wy - ay), 3)]
            frames.append(Frame(
                time=float(i),
                targets=[Target(side=SIDE, position=pos)],
                grippers=[GripperState(side=SIDE, closed=grip)],
            ))

        return TaskDescription(path.stem, frames)

    def _avg_ankle(self, row):
        right = [float(row["RIGHT_ANKLE_x"]), float(row["RIGHT_ANKLE_y"]), float(row["RIGHT_ANKLE_z"])]
        left = [float(row["LEFT_ANKLE_x"]), float(row["LEFT_ANKLE_y"]), float(row["LEFT_ANKLE_z"])]
        return [(r + l) / 2 for r, l in zip(right, left)]

    def _pinch(self, row):
        p = SIDE.upper()
        try:
            thumb = [float(row[f"{p}_THUMB_TIP_x"]), float(row[f"{p}_THUMB_TIP_y"]), float(row[f"{p}_THUMB_TIP_z"])]
            index = [float(row[f"{p}_INDEX_FINGER_TIP_x"]), float(row[f"{p}_INDEX_FINGER_TIP_y"]), float(row[f"{p}_INDEX_FINGER_TIP_z"])]
        except (KeyError, ValueError):
            return True
        return math.dist(thumb, index) < PINCH_THRESHOLD
