import csv
import math
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_level import Frame, Motion, Target, GripperState

SIDE = "right"
PINCH_THRESHOLD = 0.05
MIN_MOVE_DIST = 0.07


class MediaPipeCSVAdapter(Adapter):

    def to_motion(self, source) -> Motion:
        path = Path(source)
        with path.open() as f:
            rows = list(csv.DictReader(f))
        if not rows:
            return Motion(path.stem, [])

        # use average ankle position from first frame as floor origin
        ax, ay, _ = self._avg_ankle(rows[0])
        frames = []
        prev_grip = None
        prev_pos = None
        p = SIDE.upper()

        for i, row in enumerate(rows):
            targets, grippers = [], []

            # convert mediapipe wrist to robot frame
            try:
                wx = float(row[f"{p}_WRIST_x"])
                wy = float(row[f"{p}_WRIST_y"])
                pos = [0.5, round(wx - ax, 3), round(-(wy - ay), 3)]
            except (KeyError, ValueError):
                pos = None

            # track gripper state changes
            grip = self._pinch(row)
            if grip != prev_grip:
                grippers.append(GripperState(side=SIDE, closed=grip))
                prev_grip = grip

            # skip if wrist barely moved
            if pos and prev_pos and not grippers:
                if math.dist(pos, prev_pos) < MIN_MOVE_DIST:
                    continue

            if pos:
                targets.append(Target(side=SIDE, position=pos))
                prev_pos = pos

            if targets or grippers:
                frames.append(Frame(time=float(i), targets=targets, grippers=grippers))

        return Motion(path.stem, frames)

    # average both ankle positions as floor reference point
    def _avg_ankle(self, row):
        right = [float(row["RIGHT_ANKLE_x"]), float(row["RIGHT_ANKLE_y"]), float(row["RIGHT_ANKLE_z"])]
        left = [float(row["LEFT_ANKLE_x"]), float(row["LEFT_ANKLE_y"]), float(row["LEFT_ANKLE_z"])]
        return [(r + l) / 2 for r, l in zip(right, left)]

    # check if thumb and index finger are pinching
    def _pinch(self, row):
        p = SIDE.upper()
        try:
            thumb = [float(row[f"{p}_THUMB_TIP_x"]), float(row[f"{p}_THUMB_TIP_y"]), float(row[f"{p}_THUMB_TIP_z"])]
            index = [float(row[f"{p}_INDEX_FINGER_TIP_x"]), float(row[f"{p}_INDEX_FINGER_TIP_y"]), float(row[f"{p}_INDEX_FINGER_TIP_z"])]
        except (KeyError, ValueError):
            return True
        return math.dist(thumb, index) < PINCH_THRESHOLD
