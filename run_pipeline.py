import argparse
import importlib.util
import os
import sys
from pathlib import Path
from motion_pipeline.runtime.generate import generate_rml, generate_rml_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", type=Path)
    parser.add_argument("--adapter", choices=["json", "mediapipe_csv"], required=True)
    parser.add_argument("--robot", choices=["tiago", "nao", "ur5e"], required=True)
    parser.add_argument("--webots", action="store_true")
    parser.add_argument("--print-rml", action="store_true")
    args = parser.parse_args()

    if args.print_rml:
        rml = generate_rml(args.input_path, args.adapter, args.robot)
        print(rml)

    if args.webots:
        payload = generate_rml_payload(args.input_path, args.adapter, args.robot)
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
