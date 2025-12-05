import argparse
import importlib.util
import os
import sys
from pathlib import Path
from motion_pipeline.runtime.robot_config import RobotConfig
from motion_pipeline.runtime.retargeter import motion_to_program
from motion_pipeline.rml.converter import program_to_legacy_payload
from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter

def main():
    parser = argparse.ArgumentParser(description="Run the motion pipeline.")
    parser.add_argument("json_path", type=Path, help="Path to the input JSON file.")
    parser.add_argument("--webots", action="store_true", help="Append motion to Webots controller.")
    args = parser.parse_args()

    config = RobotConfig(
        name="TIAGo",
        chains={
            "right": ["arm_1_joint", "arm_2_joint", "arm_3_joint", "arm_4_joint", "arm_5_joint", "arm_6_joint", "arm_7_joint"]
        },
        limits={
            "arm_1_joint": (0.0, 2.67),
            "arm_2_joint": (-1.4, 1.01),
            "arm_3_joint": (-3.53, 1.5),
            "arm_4_joint": (-0.32, 2.35),
            "arm_5_joint": (-2.09, 2.09),
            "arm_6_joint": (-1.41, 1.41),
            "arm_7_joint": (-2.07, 2.07),
        },
        end_effectors={
            "right": ("torso_lift_link", "gripper_tool_link")
        },
    )

    adapter = JsonScenarioAdapter()
    motion = adapter.to_motion(args.json_path)
    program = motion_to_program(motion, config)
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
