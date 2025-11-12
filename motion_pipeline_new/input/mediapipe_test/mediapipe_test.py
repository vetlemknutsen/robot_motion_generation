import cv2, json, math
import numpy as np
import pandas as pd

from mediapipe import solutions 

mp_pose = solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, enable_segmentation=False)

cap = cv2.VideoCapture("motion_pipeline/input/mediapipe_test/shake_head.mp4") 
rows = []
frame_idx = 0

def lm_to_dict(lm):
    return {"x": lm.x, "y": lm.y, "z": lm.z, "v": lm.visibility}

keep = [
    "NOSE",
    "LEFT_SHOULDER","RIGHT_SHOULDER",
    "LEFT_ELBOW","RIGHT_ELBOW",
    "LEFT_WRIST","RIGHT_WRIST",
    "LEFT_HIP","RIGHT_HIP"
]
name_to_idx = {name:getattr(mp_pose.PoseLandmark, name).value for name in keep}

while True:
    ok, frame = cap.read()
    if not ok: break
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = pose.process(rgb)
    if res.pose_landmarks:
        lms = res.pose_landmarks.landmark
        rec = {"frame": frame_idx}
        for name, idx in name_to_idx.items():
            rec[f"{name}_x"] = lms[idx].x
            rec[f"{name}_y"] = lms[idx].y
            rec[f"{name}_z"] = lms[idx].z
            rec[f"{name}_v"] = lms[idx].visibility
        rows.append(rec)
    frame_idx += 1

cap.release()
pose.close()

df = pd.DataFrame(rows)
df.to_csv("motion_pipeline/input/mediapipe_test/shake_head.csv", index=False)
print("Wrote mediapipe_pose_subset.csv")
