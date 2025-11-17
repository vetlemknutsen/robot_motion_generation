import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.core.canonical import CanonicalFrame, CanonicalMotion, JointAngle


class JsonAdapter(Adapter):
    def to_motion(self, source: Any) -> CanonicalMotion:
        data = self._load(source)
        frames = self._collect_frames(data)
        return CanonicalMotion(
            name=data.get("name", "unnamed_motion"),
            frames=frames,
        )

    def _collect_frames(self, data: Mapping[str, Any]) -> list[CanonicalFrame]:
        raw_frames = data.get("frames")

        frames: list[CanonicalFrame] = []
        for frame_data in raw_frames:
            frames.append(
                CanonicalFrame(
                    time=float(frame_data["time"]),
                    joint_angles=[
                        self._dict_to_joint_angle(angle)
                        for angle in frame_data.get("joint_angles", [])
                    ],
                )
            )
        
        frames.sort(key=lambda frame: frame.time)
        return frames

    def _dict_to_joint_angle(self, entry: Mapping[str, Any]) -> JointAngle:
        return JointAngle(
            joint=entry["joint"],
            component=entry["component"],
            degrees=float(entry["degrees"]),
            side=entry.get("side"),
        )

    def _load(self, source: Any) -> Mapping[str, Any]:
        if isinstance(source, (str, Path)):
            with open(source) as f:
                return json.load(f)
        return source
