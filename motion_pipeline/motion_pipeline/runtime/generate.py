from pathlib import Path

import yaml

from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter
from motion_pipeline.adapters.mediapipe_csv_adapter import MediaPipeCSVAdapter
from motion_pipeline.core.joint_level import Program
from motion_pipeline.rml.rml_emitter import BasicRMLEmitter
from motion_pipeline.rml.rml_text_to_json import rml_text_to_legacy_payload
from motion_pipeline.runtime.configs.robot_config import RobotConfig
from motion_pipeline.runtime.task_to_joint import motion_to_program

ROBOTS_DIR = Path(__file__).parent / "configs" / "robots"

ADAPTERS = {
    "json" : "json",
    "mediapipe_csv" : "mediapipe_csv"
}

def build_robot_config(robot_key: str) -> RobotConfig:
    yaml_path = ROBOTS_DIR / f"{robot_key}.yaml"
    if not yaml_path.exists():
        available = [f.stem for f in ROBOTS_DIR.glob("*.yaml")]
        raise ValueError(f"Unknown robot: '{robot_key}'. Available: {available}")
    with open(yaml_path) as f:
        preset = yaml.safe_load(f)
    return RobotConfig(
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
        joint_groups=preset.get("joint_groups", {}),
    )

def build_adapter(adapter_key: str, robot: RobotConfig):
    if adapter_key=="json":
        return JsonScenarioAdapter()
    if adapter_key=="mediapipe_csv":
        return MediaPipeCSVAdapter(robot)
    raise ValueError(f"Unknown adapter: '{adapter_key}'. Available: {list(ADAPTERS.keys())}")

def generate_program(input_path: Path, adapter_key: str, robot_key: str) -> Program:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: '{input_path}'")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: '{input_path}'")

    robot = build_robot_config(robot_key)
    adapter = build_adapter(adapter_key, robot)
    try:
        motion = adapter.to_motion(input_path)
    except Exception as e:
        raise RuntimeError(
            f"Adapter '{adapter_key}' failed to parse '{input_path}': {type(e).__name__}: {e}"
        ) from e

    try:
        program = motion_to_program(motion, robot)
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert motion to program for robot '{robot_key}' "
            f"from '{input_path}': {type(e).__name__}: {e}"
        ) from e

    return program

def generate_rml(input_path: Path, adapter_key: str, robot_key: str):
    robot = build_robot_config(robot_key)

    program = generate_program(input_path, adapter_key, robot_key)

    if program.instructions:
        first = program.instructions[0]
    rml = BasicRMLEmitter(robot).emit(program)
    return rml

def generate_rml_json_from_plaintext(text: str):
    data = rml_text_to_legacy_payload(text)
    return data
