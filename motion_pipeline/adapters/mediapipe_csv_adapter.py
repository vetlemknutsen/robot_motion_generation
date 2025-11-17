import csv
from math import degrees
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.canonical import CanonicalFrame, CanonicalMotion, JointAngle


YAW_MAX_RAD = 2.09
PITCH_MIN_RAD = -0.67
PITCH_MAX_RAD = 0.51
YAW_MAX_DEG = degrees(YAW_MAX_RAD)
PITCH_MIN_DEG = degrees(PITCH_MIN_RAD)
PITCH_MAX_DEG = degrees(PITCH_MAX_RAD)


class MediaPipeCSVAdapter(Adapter):
    def to_motion(self, source) -> CanonicalMotion:
        path = Path(source)
        with path.open(newline="") as handle:
            rows = list(csv.DictReader(handle))

        if len(rows) <= 12:
            selected = rows
        else:
            count = 24
            selected = [
                rows[int(i * (len(rows) - 1) / (count - 1))]
                for i in range(count)
            ]

        processed = []
        for row in selected:
            nose_x = float(row["NOSE_x"])
            left_x = float(row["LEFT_SHOULDER_x"])
            right_x = float(row["RIGHT_SHOULDER_x"])
            width = abs(left_x - right_x) or 1.0
            center_x = (left_x + right_x) / 2
            yaw_norm = (nose_x - center_x) / (width / 2)
            yaw = max(-1, min(1, yaw_norm)) * YAW_MAX_DEG

            left_y = float(row["LEFT_SHOULDER_y"])
            right_y = float(row["RIGHT_SHOULDER_y"])
            shoulder_y = (left_y + right_y) / 2
            nose_y = float(row["NOSE_y"])
            gap = shoulder_y - nose_y
            processed.append((yaw, gap))

        gaps = [gap for _, gap in processed]
        gap_min = min(gaps) if gaps else 0.0
        gap_max = max(gaps) if gaps else 0.0
        span = gap_max - gap_min
        mid = (gap_min + gap_max) / 2 if gaps else 0.0

        frames = []
        for index, (yaw, gap) in enumerate(processed):
            if span == 0:
                pitch_norm = 0.0
            else:
                pitch_norm = (gap - mid) / (span / 2)
            pitch_norm = max(-1, min(1, pitch_norm))
            pitch = ((pitch_norm + 1) / 2) * (PITCH_MAX_DEG - PITCH_MIN_DEG) + PITCH_MIN_DEG

            frames.append(
                CanonicalFrame(
                    time=index,
                    joint_angles=[
                        JointAngle("head", "yaw", yaw),
                        JointAngle("head", "pitch", pitch),
                    ],
                )
            )

        return CanonicalMotion(path.stem, frames)
