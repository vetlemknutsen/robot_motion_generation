import csv
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.task_spec import MotionDirective, StageDefinition


class VideoAdapter(Adapter):
    """Convert MediaPipe CSV keypoints into TaskSpec stages for arm or head motions."""

    ARM_COLUMNS = [
        "RIGHT_SHOULDER_x", "RIGHT_SHOULDER_y", "RIGHT_SHOULDER_z",
        "RIGHT_ELBOW_x", "RIGHT_ELBOW_y", "RIGHT_ELBOW_z",
        "RIGHT_HIP_x", "RIGHT_HIP_y", "RIGHT_HIP_z",
        "RIGHT_WRIST_x", "RIGHT_WRIST_y", "RIGHT_WRIST_z",
    ]

    HEAD_COLUMNS = [
    "NOSE_x","NOSE_y","NOSE_z",
    "RIGHT_SHOULDER_x","RIGHT_SHOULDER_y","RIGHT_SHOULDER_z",
    ]

    JOINT_LIMITS = {
        ("right", "shoulder", "pitch"): (-2.0, 2.0),
        ("right", "shoulder", "roll"): (-1.5, 1.5),
        ("right", "elbow", "roll"): (0.6, 1.2),
        ("center", "head", "yaw"): (-1.5, 1.5),
    }

    def can_handle(self, source: Any) -> bool:
        return isinstance(source, (str, Path)) and str(source).lower().endswith(".csv")

    def to_directive(self, source: Any) -> MotionDirective:
        path = Path(source)
        frames = self._read_frames(path)
        key_indices = self._pick_key_frames(frames)

        print(self._is_head_motion(frames))
        if self._is_head_motion(frames):
            baseline = frames[0]["NOSE_x"]
            stages = self._emit_head_stages(frames, key_indices, baseline)
            if not stages:
                stages = self._emit_arm_stages(frames, key_indices)
        else:
            stages = self._emit_arm_stages(frames, key_indices)

        if not stages:
            raise ValueError("Video adapter could not extract any valid poses.")

        # add a simple reset stage
        stages.append(self._reset_stage())

        return MotionDirective(
            name=path.stem,
            source=None,
            destination=None,
            objects=[],
            stages=stages,
        )

    # ------------------------------------------------------------------ common helpers

    def _read_frames(self, path: Path) -> List[Dict[str, float]]:
        with path.open() as f:
            reader = csv.DictReader(f)
            frames = []
            for row in reader:
                frames.append({k: float(v) for k, v in row.items() if v})
        return frames

    def _pick_key_frames(self, frames: Sequence[Dict[str, float]], max_points: int = 12) -> List[int]:
        total = len(frames)
        if total == 0:
            return []

        def wrist_x(i: int) -> float:
            return frames[i].get("RIGHT_WRIST_x", 0.0)

        indices = {0, total - 1}
        if total > 2:
            max_idx = max(range(total), key=wrist_x)
            min_idx = min(range(total), key=wrist_x)
            indices.update({max_idx, min_idx})

        if total > len(indices):
            step = max(1, total // max_points)
            for i in range(0, total, step):
                indices.add(i)
                if len(indices) >= max_points:
                    break

        return sorted(indices)

    def _clamp(self, value: float, key) -> float:
        low, high = self.JOINT_LIMITS.get(key, (-3.0, 3.0))
        return max(low, min(high, value))

    # ------------------------------------------------------------------ arm mode

    def _emit_arm_stages(self, frames, key_indices) -> List[StageDefinition]:
        stages = []
        for idx in key_indices:
            frame = frames[idx]
            if not all(col in frame for col in self.ARM_COLUMNS):
                continue

            shoulder = self._vec(frame, "RIGHT_SHOULDER")
            hip = self._vec(frame, "RIGHT_HIP")
            elbow = self._vec(frame, "RIGHT_ELBOW")

            shoulder_pitch = self._clamp(
                self._angle_pitch(hip, shoulder, elbow),
                ("right", "shoulder", "pitch"),
            )
            shoulder_roll = self._clamp(
                self._angle_roll(shoulder, elbow),
                ("right", "shoulder", "roll"),
            )

            moves = [
                {"type": "move", "side": "right", "joint": "shoulder", "rotation": "pitch", "position": shoulder_pitch},
                {"type": "move", "side": "right", "joint": "shoulder", "rotation": "roll", "position": shoulder_roll},
                {"type": "move", "side": "right", "joint": "elbow", "rotation": "roll", "position": self._clamp(1.0, ("right", "elbow", "roll"))},
            ]
            stages.append(StageDefinition(name=f"pose_{idx}", instructions=[{"type": "multi", "moves": moves}]))
        return stages

    # ------------------------------------------------------------------ head mode

    def _is_head_motion(self, frames: Sequence[Dict[str, float]], threshold: float = 0.05) -> bool:
        if not frames:
            return False
        if not all(col in frames[0] for col in self.HEAD_COLUMNS):
            return False
        nose_x = [frame["NOSE_x"] for frame in frames]
        return max(nose_x) - min(nose_x) > threshold

    def _emit_head_stages(self, frames, key_indices, baseline_x) -> List[StageDefinition]:
        stages = []
        for idx in key_indices:
            frame = frames[idx]
            if not all(col in frame for col in self.HEAD_COLUMNS):
                continue

            nose = self._vec(frame, "NOSE")
            head_yaw = self._clamp(
                self._head_yaw(nose[0], baseline_x),
                ("head", "yaw"),
            )
            stages.append(
                StageDefinition(
                    name=f"pose_{idx}",
                    instructions=[
                        {
                            "type": "move",
                            "joint": "head",
                            "rotation": "yaw",
                            "position": head_yaw,
                        }
                    ],
                )
            )
        return stages


    # ------------------------------------------------------------------ reset

    def _reset_stage(self) -> StageDefinition:
        return StageDefinition(
            name="reset",
            instructions=[
                {
                    "type": "multi",
                    "moves": [
                        {"type": "move", "side": "right", "joint": "shoulder", "rotation": "pitch", "position": 1.5},
                        {"type": "move", "side": "right", "joint": "shoulder", "rotation": "roll", "position": 0.0},
                        {"type": "move", "side": "right", "joint": "elbow", "rotation": "roll", "position": 0.8},
                        {"type": "move", "joint": "head", "rotation": "pitch", "position": 0.0},
                    ],
                }
            ],
        )

    # --- math helpers ------------------------------------------------------

    def _vec(self, frame, key):
        return frame[f"{key}_x"], frame[f"{key}_y"], frame[f"{key}_z"]

    def _head_yaw(self, nose_x: float, baseline_x: float) -> float:
        displacement = nose_x - baseline_x
        # map displacement into joint limits
        yaw = displacement * 4.0  # e.g. self.HEAD_GAIN = 4.0
        return max(-0.6, min(0.6, yaw))

    
    def _nose_center(self, frames) -> float:
        values = [frame.get("NOSE_x", 0.0) for frame in frames]
        return sum(values) / len(values) if values else 0.0




    def _angle_roll(self, shoulder, elbow):
        # horizontal swing of shoulder->elbow
        sx, sy, sz = shoulder
        ex, ey, ez = elbow
        dx = ex - sx
        dz = ez - sz
        return math.atan2(dx, abs(dz) + 1e-6)

    def _angle_pitch(self, root, joint, target):
        # project joint->target and joint->root onto the vertical plane
        jx, jy, jz = joint
        tx, ty, tz = target
        rx, ry, rz = root
        u = (ty - jy, tz - jz)
        v = (jy - ry, jz - rz)
        dot = u[0] * v[0] + u[1] * v[1]
        nu = math.sqrt(u[0] ** 2 + u[1] ** 2)
        nv = math.sqrt(v[0] ** 2 + v[1] ** 2)
        if nu * nv == 0:
            return 0.0
        cos_angle = max(-1.0, min(1.0, dot / (nu * nv)))
        return math.pi / 2 - math.acos(cos_angle)
