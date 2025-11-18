import csv
from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.motion import PoseFrame, MotionSequence, JointAngle


# Human-like head ranges
YAW_MAX = 90
PITCH_MAX = 60
PITCH_GAIN = 2


class MediaPipeCSVAdapter(Adapter):
    def to_motion(self, source) -> MotionSequence:
        rows = list(csv.DictReader(Path(source).open(newline="")))
        # At most 24 frames
        if len(rows) > 12:
            step = max(1, len(rows) // 24)
            rows = rows[::step]

        neutral_gap = None
        frames = []
        for i, row in enumerate(rows):
            # Estimate yaw by findinging nose x position and left/right shoulder x positions.
            nx = float(row["NOSE_x"])
            lx = float(row["LEFT_SHOULDER_x"])
            rx = float(row["RIGHT_SHOULDER_x"])
            width = abs(lx - rx) or 1.0 

            # Shoulder midpoint
            cx = (lx + rx) / 2
            # How far the nose is from the center
            yaw_norm = (nx - cx) / (width / 2) 
            yaw = max(-1, min(1, yaw_norm)) * YAW_MAX

            
            ly = float(row["LEFT_SHOULDER_y"])
            ry = float(row["RIGHT_SHOULDER_y"])
            # Average shoulder height
            cy = (ly + ry) / 2
            ny = float(row["NOSE_y"])
            # Compare shoulder height to nose height
            gap = cy - ny

            if neutral_gap is None: 
                neutral_gap = gap 
            
            pitch_norm = (gap - neutral_gap) / (width or 1.0)
            pitch_norm *= PITCH_GAIN
            pitch_norm = max(-1, min(1, pitch_norm))
            pitch = pitch_norm * PITCH_MAX
       
            frames.append(
                PoseFrame(
                    time=i,
                    joint_angles=[
                        JointAngle("head", "yaw", yaw),
                        JointAngle("head", "pitch", pitch),
                    ],
                )
            )

        return MotionSequence(Path(source).stem, frames)
