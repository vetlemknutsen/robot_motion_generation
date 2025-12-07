import argparse
import importlib.util
import os
import sys
from pathlib import Path
from motion_pipeline.runtime.robot_config import RobotConfig
from motion_pipeline.runtime.retargeter import motion_to_program
from motion_pipeline.rml.converter import program_to_legacy_payload
from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter
from motion_pipeline.runtime.robots import TIAGO

def main():
    parser = argparse.ArgumentParser(description="Run the motion pipeline.")
    parser.add_argument("input_path", type=Path, help="Path to the input file.")
    parser.add_argument("--adapter", choices=["json", "mediapipe_csv"], default="json", help="Which adapter to use.")
    parser.add_argument("--webots", action="store_true", help="Append motion to Webots controller.")
    args = parser.parse_args()

    robot = RobotConfig(
        name=TIAGO["name"],
        chains=TIAGO["chains"],
        limits=TIAGO["limits"],
        end_effectors=TIAGO["end_effectors"],
        grippers=TIAGO["grippers"]
    )

    adapter = JsonScenarioAdapter() if args.adapter == "json" else MediaPipeCSVAdapter()
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
