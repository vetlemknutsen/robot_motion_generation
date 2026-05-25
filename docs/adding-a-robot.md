# Adding a New Robot

Adding a robot has three parts: MoveIt package, pipeline YAML config, and execution-side joint mapping.

## 1. Add MoveIt config package (required)

The generator launches:

`ros2 launch <robot>_moveit_config move_group.launch.py`

So package name must match the robot key:

- key: `myrobot`
- package: `myrobot_moveit_config`

Recommended workflow (same style as existing robots in `ros_ws/src/robots/*_ws`):

1. Use MoveIt Setup Assistant with your robot URDF.
2. Generate `<robot>_moveit_config`.
3. Place it under:
   `ros_ws/src/robots/<robot>_ws/src/<robot>_moveit_config/`

## 2. Add pipeline robot config (required)

Create a YAML file in:

`motion_pipeline/motion_pipeline/pipeline/configs/robots/`

The filename is the robot key used by the backend. Example:

- file: `myrobot.yaml`
- key: `myrobot`

The key is lowercase (the GUI lowercases robot names before sending) and matches the filename, which is how the backend finds the robot at runtime.

This YAML specifies what URDF and SRDF don't, like which joint plays the role of right shoulder pitch, what radian values count as gripper open/closed, what orientation to fall back on when the input has none, and what posture to seed IK with.

Required fields:
- `name`: Used for user-facing logs/messages (display name in generator output).
- `moveit_group`: The MoveIt planning group (a named set of joints/links, for example one arm) that IK/planning should run on.
- `base_frame`: The coordinate frame used for input target positions before they are sent to IK.
- `chains`: In principle this can be derived from MoveIt group joints, but this pipeline keeps it explicit so you can control exactly which joints are emitted and in what order.
- `end_effectors`: Provides the tip link required by IK requests for each side.
- `joint_groups`: Required so the emitter can translate joint names into valid RML command tokens (`move <side> <group> <rotation> ...`). Without this mapping, joint moves are not emitted as executable RML.

Optional fields:
- `grippers`: Per-side gripper joints and numeric open/closed values to emit for gripper actions.
- `default_orientation`: Quaternion used when a target has no explicit orientation.
- `orientation_options`: List of fallback quaternions to try if IK fails with the first orientation.
- `base_offset`: Used to convert world-referenced input positions into the robot `base_frame` used by IK. Needed when the robot base frame origin is offset (for example above ground, like a torso-level frame).
- `ik_seed`: Initial joint values used to bias IK toward a preferred posture.

`joint_groups` format is nested mapping, not list:

```yaml
joint_groups:
  right:
    shoulder:
      pitch: joint1
      roll: joint2
    elbow:
      pitch: joint3
    wrist:
      yaw: joint4
```

Add a `left` side (under `chains`, `end_effectors`, `joint_groups`, and `grippers`) only when your input actually uses it. If the input only uses one hand, having just `right` is enough.

## 3. Add execution-side joint mapping (required to execute motions)

RML/joint descriptions use abstract names (`shoulder`, `elbow`, etc.), so you need a mapping layer to actual robot interfaces.

For Webots in this repo:

1. Add mapping:
   `webots/controllers/robot_controller/configs/myrobot.yaml`
2. Set active robot:
   `webots/controllers/robot_controller/config.yaml`
3. If needed, add world:
   `webots/worlds/myrobot.wbt`

For a real robot, provide an equivalent mapping in the execution bridge/controller that consumes generated commands.

## 4. Add to GUI dropdown

Edit:

`ros_ws/src/qt_gui/ui/main_window.ui`

Add robot text in `robotBox` (Qt Designer or XML). Any casing is fine for display; request is lowercased before backend call.

## 5. Build and test

```bash
colcon build
source install/setup.bash
ros2 launch motion_pipeline_bringup pipeline.launch.py
```
