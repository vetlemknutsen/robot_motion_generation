import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

from motion_pipeline.adapters.json_adapter import JsonAdapter
from motion_pipeline.adapters.video_adapter import VideoAdapter
from motion_pipeline.emitter.emitter import BasicRMLEmitter
from motion_pipeline.rml.converter import program_to_legacy_payload
from motion_pipeline.runtime.task_spec_to_program import task_spec_to_program
from motion_pipeline.validator.langium import LangiumRMLValidator


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    motions_dir = project_root / "motion_pipeline" / "input"
    langium_root = project_root / "robot-motion-language"

    parser = argparse.ArgumentParser()
    parser.add_argument("--motion", default="simple_wave", help="Name of motion template (json) or BVH filename.")
    args = parser.parse_args()

    directive = _load_task_spec(motions_dir, args.motion)

    program = task_spec_to_program(directive)
 
    emitter = BasicRMLEmitter()
    rml_text = emitter.emit(program)
    print("RML")
    print(rml_text)

    validator = LangiumRMLValidator(langium_root)
    validator.validate(rml_text)
    print("\nRML validated by Langium.")


    legacy_payload = program_to_legacy_payload(program)
    print(legacy_payload)

    append_motion_to_webots(legacy_payload)
    print("Motion appended to motion_functions.py")


def _load_task_spec(motions_dir: Path, motion_arg: str):
    motion_path = Path(motion_arg)
    if motion_path.suffix.lower() == ".csv":
        path = motion_path if motion_path.is_absolute() else motions_dir / motion_path
        return VideoAdapter().to_directive(path)

    if not motion_path.suffix:
        motion_path = motion_path.with_suffix(".json")
    path = motion_path if motion_path.is_absolute() else motions_dir / motion_path
    payload = load_motion(path)
    adapter = JsonAdapter()
    return adapter.to_directive(payload)


def load_motion(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


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
