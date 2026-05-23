# Installation

Requires Ubuntu 24.04.

## 1. System packages

ROS 2 Jazzy. Follow the official guide at https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

Then install colcon, Qt6, Nodejs, npm, MoveIt and ik plugin. 

```bash
sudo apt install python3-colcon-common-extensions qt6-base-dev qt6-tools-dev nodejs npm ros-jazzy-trac-ik-kinematics-plugin ros-jazzy-moveit
```

## 2. Webots

Install Webots from https://cyberbotics.com/doc/guide/installation-procedure

## 3. Python dependencies

Run from the repo root.

```bash
pip install -r requirements.txt
pip install -e motion_pipeline --break-system-packages
```

The second command installs the `motion_pipeline` package in editable mode so the ROS bridge can import it. --break-system-packages to avoid virtual env.

## 4. Build the Langium RML parser

The pipeline shells out to a Langium-based CLI to parse RML.

```bash
cd robot-motion-language
npm install
npm run langium:generate
npm run build
cd ..
```

## 5. OpenAI API key (optional)

The pipeline labels generated RML using an LLM. To enable this, put your key in a `.env` file at the repo root.

```
OPENAI_API_KEY=sk-...
```

If you don't want labeling, comment out the import on [pipeline.py:14](motion_pipeline/motion_pipeline/pipeline/pipeline.py#L14) and the two labeler calls on [pipeline.py:96-97](motion_pipeline/motion_pipeline/pipeline/pipeline.py#L96-L97).

## 6. Build

Run colcon build from `ros_ws`.

```bash
cd ros_ws
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

For TIAGo, you also need PAL packages like `tiago_description` and `pal_gripper_description` from PAL's apt repos. They are not in the repo and not part of stock Jazzy.

## 7. Run

```bash
ros2 launch motion_pipeline_bringup pipeline.launch.py
```

To start Webots with ROS sourced, run the wrapper script at the repo root.

```bash
./webots_ros2.sh
```

---

This guide has not been tested end to end and may be missing steps. If you find something missing, feel free to add it.
