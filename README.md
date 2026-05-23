# Robot Motion Generation

A pipeline that turns motion inputs (recorded video keypoints, hand-authored JSON, and other sources) into executable robot motion programs written in RML (Robot Motion Language). Generated programs can be run in Webots or sent to a real robot through an execution bridge.

## Quickstart

After [installation](docs/installation.md), launch the pipeline.

```bash
ros2 launch motion_pipeline_bringup pipeline.launch.py
```

The Qt GUI opens. Pick an input file, choose an adapter and a robot, then generate.

## Repo layout

- `motion_pipeline/` holds the Python pipeline (adapters, IK, RML emitter, robot configs).
- `ros_ws/` is the ROS 2 workspace (GUI, bridge node, per-robot MoveIt packages).
- `webots/` has the Webots worlds and the controller that consumes generated RML.
- `robot-motion-language/` contains the Langium grammar and CLI for RML parsing.
- `docs/` has guides for installation, adding robots, and adding adapters.

## Supported today

Robots
- NAO
- TIAGo
- PR2
- UR5e

Input adapters
- JSON (`json`)
- MediaPipe CSV (`mediapipecsv`)

## Extending

- [Adding a new robot](docs/adding-a-robot.md)
- [Adding a new input format](docs/adding-an-adapter.md)
