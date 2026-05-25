from pathlib import Path

from motion_pipeline.adapters.base import Adapter
import motion_pipeline.adapters
from motion_pipeline.adapters.base import ADAPTERS
from motion_pipeline.rml.base import Emitter
import yaml

from motion_pipeline.types.JointDescription import JointDescription
from motion_pipeline.rml.rml_emitter import BasicRMLEmitter
from motion_pipeline.rml.rml_text_to_json import LangiumRMLParser
from motion_pipeline.pipeline.configs.robot_config import RobotConfig
from motion_pipeline.pipeline.transformer import taskdescription_to_jointdescription
from motion_pipeline.llm.llm_labeler import LLMLabeler

from motion_pipeline.kinematics.ik_solver import MoveItIKClient

# Folder where per-robot YAML configs live. Filename (without .yaml) is the robot key.
ROBOTS_DIR = Path(__file__).parent / "configs" / "robots"

# Registry of output formats. Add new ones here
EMITTERS: dict[str, type[Emitter]] = {
    "rml": BasicRMLEmitter,
}


def load_robot_config(robot_key: str) -> RobotConfig:
    """Load a robot's YAML config and return it as a RobotConfig.
    Args:
        robot_key: Filename (without .yaml) of the robot in configs/robots/.
    Returns:
        A populated RobotConfig.
    Raises:
        ValueError: If no YAML matches robot_key. The error message
            includes the list of available robots.
    """
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
        ik_seed=preset.get("ik_seed", {})
    )

# Look up an adapter class by its registered key and instantiate it
def create_adapter(adapter_key: str) -> Adapter:
    cls = ADAPTERS.get(adapter_key)
    if cls is None: 
        raise ValueError(f"Unknown adapter: '{adapter_key}'. Available: {list(ADAPTERS.keys())}")
    return cls()


def to_joint_description(input_path: Path, adapter_key: str, robot_key: str, node) -> JointDescription:
    """Convert an input file into a joint-space JointDescription.
    This is the part of the pipeline that runs before emission and
    labeling. Useful on its own if you want the joint program without
    the RML text.
    Args:
        input_path: Path to the input motion file.
        adapter_key: Key of a registered adapter.
        robot_key: Name of a robot YAML in configs/robots/.
        node: rclpy node for the IK client.
    Returns:
        Tuple of (program, skipped, total). program is a JointDescription.
    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If the path is not a file or the keys are unknown.
        RuntimeError: If parsing or IK conversion fails.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: '{input_path}'")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: '{input_path}'")

    robot = load_robot_config(robot_key)
    adapter = create_adapter(adapter_key)

    # wrap parsing errors so the user knows which adapter failed and what it failed on
    try:
        motion = adapter.to_taskdescription(input_path)
    except Exception as e:
        raise RuntimeError(
            f"Adapter '{adapter_key}' failed to parse '{input_path}': {type(e).__name__}: {e}"
        ) from e
    
    # grab the first end-effector's tip link to point IK at
    # For now we assume a single arm, if dual arm loop here
    _, tip = list(robot.end_effectors.values())[0]
    ik = MoveItIKClient(
        node,
        group_name=robot.get_group_name(),
        base_frame=robot.get_base_frame(),
        ee_link=tip
    )

    try:
        program, skipped, total = taskdescription_to_jointdescription(motion, robot, ik)
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert taskdescription to jointdescription for robot '{robot_key}' "
            f"from '{input_path}': {type(e).__name__}: {e}"
        ) from e

    return program, skipped, total



def run_pipeline(input_path: Path, adapter_key: str, robot_key: str, node, emitter_key = "rml") -> str:
    """Run the full motion pipeline end-to-end.
    Parses an input file with the chosen adapter, solves IK against the
    given robot, emits the joint-space program as text, and asks the LLM
    to add intent labels.
    Args:
        input_path: Path to the input motion file.
        adapter_key: Key of a registered adapter, e.g. "json" or "mediapipecsv".
        robot_key: Name of a robot YAML in configs/robots/ (without the .yaml).
        node: An rclpy node used by the IK client to call MoveIt.
        emitter_key: Output format key. Currently only "rml" is registered.
    Returns:
        Tuple of (rml_text, skipped, total) where rml_text is the labeled
        RML program, skipped is the number of frames IK could not reach,
        and total is the number of frames attempted.
    Raises:
        FileNotFoundError: If input_path does not exist.
        ValueError: If adapter_key, robot_key, or emitter_key is unknown.
        RuntimeError: If the adapter or IK transformer fails.
    """

    robot = load_robot_config(robot_key)
    program, skipped, total = to_joint_description(input_path, adapter_key, robot_key, node)

    emitter_cls = EMITTERS.get(emitter_key)
    if emitter_cls is None:
        raise ValueError(f"Unknown emitter: '{emitter_key}'. Available: {list(EMITTERS.keys())}")
    emitter = emitter_cls(robot)
    rml_text = emitter.emit(program)
    labeler = LLMLabeler()
    rml_text = labeler.label_code(rml_text, robot_key)
    return rml_text, skipped, total
   
# convenience. take RML text through the Langium parser to get JSON
def rml_to_json(text: str) -> dict:
    parser = LangiumRMLParser()
    return parser.parse(text)
