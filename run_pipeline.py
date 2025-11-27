import json
import argparse
from pathlib import Path
from motion_pipeline.runtime.robot_config import RobotConfig
from motion_pipeline.runtime.retargeter import motion_to_program
from motion_pipeline.rml.converter import program_to_legacy_payload
import importlib.util
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Run the motion pipeline end-to-end.")
    parser.add_argument("csv_path", type=Path, help="Path to the input MediaPipe CSV file.")
    parser.add_argument("--urdf", type=Path, default=Path("motion_pipeline/runtime/nao_robot_v4.urdf"), help="Path to the robot URDF file.")
    parser.add_argument("--webots", action="store_true", help="Append motion to Webots controller.")
    parser.add_argument("--robot", choices=["nao", "tiago"], default="nao", help="Target robot to generate motion for.")
    
    args = parser.parse_args()
    
    if args.robot == "nao":
        urdf_path = args.urdf.resolve()
        config = RobotConfig(
            name="NAO",
            urdf_path=urdf_path,
            chains={
                "left": ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"],
                "right": ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"],
                # Whole-body chains (arms + legs for automatic crouching)
                "left_with_legs": [
                    "LHipPitch", "LKneePitch", "LAnklePitch",  # Left leg
                    "RHipPitch", "RKneePitch", "RAnklePitch",  # Right leg (for balance)
                    "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw"  # Left arm
                ],
                "right_with_legs": [
                    "LHipPitch", "LKneePitch", "LAnklePitch",  # Left leg
                    "RHipPitch", "RKneePitch", "RAnklePitch",  # Right leg
                    "RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"  # Right arm
                ]
            },
            limits={
                # Arm limits
                "LShoulderPitch": (-2.085, 2.085),
                "LShoulderRoll": (-0.314, 1.326),
                "LElbowYaw": (-2.085, 2.085),
                "LElbowRoll": (-1.544, 0.0),
                "LWristYaw": (-1.823, 1.823),
                "RShoulderPitch": (-2.085, 2.085),
                "RShoulderRoll": (-1.326, 0.314),
                "RElbowYaw": (-2.085, 2.085),
                "RElbowRoll": (0.0, 1.544),
                "RWristYaw": (-1.823, 1.823),
                # Leg limits
                "LHipPitch": (-1.773, 0.740),
                "LKneePitch": (-0.092, 2.112),
                "LAnklePitch": (-1.189, 0.922),
                "RHipPitch": (-1.773, 0.740),
                "RKneePitch": (-0.092, 2.112),
                "RAnklePitch": (-1.189, 0.922),
            }
        )
    elif args.robot == "tiago":
        urdf_path = Path("motion_pipeline/runtime/urdf/tiago_steel.urdf").resolve()
        config = RobotConfig(
            name="TIAGo",
            urdf_path=urdf_path,
            chains={
                # TIAGo has a prismatic torso lift joint + 7-DOF arm
                "right": [
                    "torso_lift_joint",  # Prismatic joint (0.0 to 0.35m)
                    "arm_1_joint", "arm_2_joint", "arm_3_joint",
                    "arm_4_joint", "arm_5_joint", "arm_6_joint", "arm_7_joint"
                ],
                # Map 'left' requests to right arm (TIAGo has 1 arm)
                "left": [
                    "torso_lift_joint",
                    "arm_1_joint", "arm_2_joint", "arm_3_joint",
                    "arm_4_joint", "arm_5_joint", "arm_6_joint", "arm_7_joint"
                ]
            },
            limits={
                "torso_lift_joint": (0.0, 0.35),
                "arm_1_joint": (0.0, 2.67),  # Shoulder lift
                "arm_2_joint": (-1.4, 1.01), # Shoulder pan
                "arm_3_joint": (-3.53, 1.5),  # Elbow lift (Webots max 1.5)
                "arm_4_joint": (-0.32, 2.35), # Elbow pan (Webots min -0.32)
                "arm_5_joint": (-2.09, 2.09), # Wrist 1
                "arm_6_joint": (-1.41, 1.41), # Wrist 2
                "arm_7_joint": (-2.07, 2.07), # Wrist 3 (Webots min -2.07)
            }
        )
    
    file_ext = args.csv_path.suffix.lower()
    
    if file_ext == ".json":
        from motion_pipeline.adapters.symbolic_json_adapter import JsonScenarioAdapter
        adapter = JsonScenarioAdapter()
    elif file_ext == ".csv":
        from motion_pipeline.adapters.mediapipe_csv_adapter import MediaPipeCSVAdapter
        adapter = MediaPipeCSVAdapter()
    else:
        print(f"Error: Unsupported file type '{file_ext}'. Use .json or .csv")
        return
    
    motion = adapter.to_motion(args.csv_path)
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
