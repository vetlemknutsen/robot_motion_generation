import argparse
import importlib.util
import os
import sys
from pathlib import Path
from motion_pipeline.runtime.robot_config import RobotConfig
from motion_pipeline.runtime.retargeter import motion_to_program
from motion_pipeline.rml.converter import program_to_legacy_payload
from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter
from motion_pipeline.adapters.mediapipe_csv_adapter import MediaPipeCSVAdapter
from motion_pipeline.runtime.robots import TIAGO, NAO, UR5E

ROBOT_PRESETS = {
    "tiago" : TIAGO,
    "nao" : NAO,
    "ur5e" : UR5E
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--adapter", choices=["json", "mediapipe_csv"])
    parser.add_argument("--robot", choices=ROBOT_PRESETS.keys())
    parser.add_argument("--webots", action="store_true")
    args = parser.parse_args()

    preset = ROBOT_PRESETS[args.robot]
    robot = RobotConfig(
        name=preset["name"],
        chains=preset["chains"],
        limits=preset["limits"],
        workspace_limits=preset.get("workspace_limits", {}),
        end_effectors=preset["end_effectors"],
        grippers=preset.get("grippers", {}),
        default_orientation=preset.get("default_orientation"),
        orientation_options=preset.get("orientation_options"),
        moveit_group=preset["moveit_group"],
        base_frame=preset["base_frame"],
    )

    adapter = JsonScenarioAdapter() if args.adapter == "json" else MediaPipeCSVAdapter(robot)
    motion = adapter.to_motion(args.input_path)
    program = motion_to_program(motion, robot)
    payload = program_to_legacy_payload(program)
    if args.webots:
        append_motion_to_webots(payload)

def append_motion_to_webots(payload: dict) -> None:
    controller_dir = Path(__file__).resolve().parent / "webots" / "controllers" / "robot_controller"
    sys.path.insert(0, str(controller_dir))
    prev_cwd = os.getcwd()
    try:
        os.chdir(controller_dir)
        spec = importlib.util.spec_from_file_location("legacy_helpers", controller_dir / "helpers.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.createNewMotion(payload)
    finally:
        os.chdir(prev_cwd)
        sys.path.pop(0)

if __name__ == "__main__":
    main()
