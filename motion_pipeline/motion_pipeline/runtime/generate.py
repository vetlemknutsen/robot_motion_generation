from pathlib import Path

from motion_pipeline.adapters.base import Adapter
from motion_pipeline.rml.base import Emitter
import yaml

from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter
from motion_pipeline.adapters.mediapipe_csv_adapter import MediaPipeCSVAdapter
from motion_pipeline.core.joint_level import JointDescription
from motion_pipeline.rml.rml_emitter import BasicRMLEmitter
from motion_pipeline.rml.rml_text_to_json import LangiumRMLParser
from motion_pipeline.runtime.configs.robot_config import RobotConfig
from motion_pipeline.runtime.task_to_joint import taskdescription_to_jointdescription
from motion_pipeline.llm.llm_labeler import LLMLabeler

from motion_pipeline.kinematics.ik_solver import MoveItIKClient

ROBOTS_DIR = Path(__file__).parent / "configs" / "robots"

ADAPTERS: dict[str, type[Adapter]] = {
    "json": JsonScenarioAdapter,
    "mediapipecsv": MediaPipeCSVAdapter,
}

EMITTERS: dict[str, type[Emitter]] = {
    "rml": BasicRMLEmitter,
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
        end_effectors=preset["end_effectors"],
        grippers=preset.get("grippers", {}),
        default_orientation=preset.get("default_orientation"),
        orientation_options=preset.get("orientation_options"),
        moveit_group=preset["moveit_group"],
        base_frame=preset["base_frame"],
        joint_groups=preset.get("joint_groups", {}),
        base_offset=preset.get("base_offset", [0.0, 0.0, 0.0]),
    )

def build_adapter(adapter_key: str) -> Adapter:
    cls = ADAPTERS.get(adapter_key)
    if cls is None: 
        raise ValueError(f"Unknown adapter: '{adapter_key}'. Available: {list(ADAPTERS.keys())}")
    return cls()


def generate_jointdescription(input_path: Path, adapter_key: str, robot_key: str, node) -> JointDescription:
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: '{input_path}'")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: '{input_path}'")

    robot = build_robot_config(robot_key)
    adapter = build_adapter(adapter_key)

    try:
        motion = adapter.to_taskdescription(input_path)
    except Exception as e:
        raise RuntimeError(
            f"Adapter '{adapter_key}' failed to parse '{input_path}': {type(e).__name__}: {e}"
        ) from e
    
    _, tip = list(robot.end_effectors.values())[0]
    ik = MoveItIKClient(
        node,
        group_name=robot.get_group_name(),
        base_frame=robot.get_base_frame(),
        ee_link=tip
    )

    try:
        program = taskdescription_to_jointdescription(motion, robot, ik)
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert taskdescription to jointdescription for robot '{robot_key}' "
            f"from '{input_path}': {type(e).__name__}: {e}"
        ) from e

    return program

def generate_output(input_path: Path, adapter_key: str, robot_key: str, node, emitter_key = "rml") -> str:
    robot = build_robot_config(robot_key)
    program = generate_jointdescription(input_path, adapter_key, robot_key, node)

    emitter_cls = EMITTERS.get(emitter_key)
    if emitter_cls is None:
        raise ValueError(f"Unknown emitter: '{emitter_key}'. Available: {list(EMITTERS.keys())}")
    emitter = emitter_cls(robot)
    rml_text = emitter.emit(program)
    labeler = LLMLabeler()
    rml_text = labeler.label_code(rml_text, robot_key)
    return rml_text
   

def generate_rml_json_from_plaintext(text: str) -> dict:
    parser = LangiumRMLParser()
    return parser.parse(text)
