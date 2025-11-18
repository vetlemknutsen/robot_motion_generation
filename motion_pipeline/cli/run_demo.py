import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

from motion_pipeline.adapters import MediaPipeCSVAdapter
from motion_pipeline.runtime import retargeter
from motion_pipeline.emitter.emitter import BasicRMLEmitter
from motion_pipeline.rml.converter import program_to_legacy_payload
from motion_pipeline.validator.langium import LangiumRMLValidator

# full ipeline script 

def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    motions_dir = project_root / "motion_pipeline" / "input"
    langium_root = project_root / "robot-motion-language"

    parser = argparse.ArgumentParser()
    parser.add_argument("--motion", default="simple_wave")
    parser.add_argument("--format", choices=("json", "csv"), default="json")
    args = parser.parse_args()

    motion_path = motions_dir / f"{args.motion}.{args.format}"

    motion_adapter = MediaPipeCSVAdapter()
    motion = motion_adapter.to_motion(motion_path)

    program = retargeter.motion_to_program(motion)
 
    emitter = BasicRMLEmitter()
    rml_text = emitter.emit(program)

    # Print RML
    print("RML")
    print(rml_text)

    # Validate RML
    validator = LangiumRMLValidator(langium_root)
    validator.validate(rml_text)
    print("RML validated by Langium.")

    # RML in JSON
    rml_payload = program_to_legacy_payload(program)
    print(rml_payload)

    # Send RML JSON payload to helper to create a new motion
    append_motion_to_webots(rml_payload)
    print("Motion appended to motion_functions.py")



def load_motion(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


# Use helper from previous thesis to add new motion
def append_motion_to_webots(payload: dict) -> None:
    controller_dir = Path(__file__).resolve().parents[2] / "webots" / "controllers" / "robot_controller"
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
