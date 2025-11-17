import csv
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.canonical import CanonicalFrame, CanonicalMotion, JointAngle


YAW_MAX = 90
PITCH_MAX = 60


class MediaPipeCSVAdapter(Adapter):
    def to_motion(self, source) -> CanonicalMotion:
        rows = list(csv.DictReader(Path(source).open(newline="")))
        if len(rows) > 12:
            step = max(1, len(rows) // 24)
            rows = rows[::step]

        gaps = []
        yaw_pitch = []
        for row in rows:
            nx = float(row["NOSE_x"])
            lx = float(row["LEFT_SHOULDER_x"])
            rx = float(row["RIGHT_SHOULDER_x"])
            width = abs(lx - rx) or 1.0
            cx = (lx + rx) / 2
            yaw_norm = (nx - cx) / (width / 2)
            yaw = max(-1, min(1, yaw_norm)) * YAW_MAX

            ly = float(row["LEFT_SHOULDER_y"])
            ry = float(row["RIGHT_SHOULDER_y"])
            cy = (ly + ry) / 2
            ny = float(row["NOSE_y"])
            gap = cy - ny
            gaps.append(gap)
            yaw_pitch.append((yaw, gap))

        if gaps:
            mid = (min(gaps) + max(gaps)) / 2
            span = (max(gaps) - min(gaps)) or 1
        else:
            mid = 0
            span = 1

        frames = []
        for i, (yaw, gap) in enumerate(yaw_pitch):
            pitch_norm = (gap - mid) / (span / 2)
            pitch = max(-1, min(1, pitch_norm)) * PITCH_MAX
            frames.append(
                CanonicalFrame(
                    time=i,
                    joint_angles=[
                        JointAngle("head", "yaw", yaw),
                        JointAngle("head", "pitch", pitch),
                    ],
                )
            )

        return CanonicalMotion(Path(source).stem, frames)
