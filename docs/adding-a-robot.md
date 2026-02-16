# Adding a New Robot

Adding a robot involves three areas: the motion pipeline config, the MoveIt setup, and the Webots simulation.

## 1. Motion pipeline config (required)

Create a YAML file in `motion_pipeline/motion_pipeline/runtime/configs/robots/`.

The filename is the robot key used everywhere (GUI, MoveIt launch, etc). For example, `myrobot.yaml` means the key is `myrobot`.

Copy an existing config (e.g. `nao.yaml`) and fill in the values. See `robot_config.py` for what each field means. The required fields are:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Display name | `"MyRobot"` |
| `moveit_group` | MoveIt planning group name | `"right_arm"` |
| `base_frame` | TF base frame | `"base_link"` |
| `chains` | Joints per side | `right: [joint1, joint2, ...]` |
| `end_effectors` | Base + tip link per side (for IK) | `right: [base_link, tool0]` |
| `joint_groups` | Abstract joint grouping for RML | see below |

`joint_groups` maps joints to abstract names used in RML. For example:
```yaml
joint_groups:
  right:
    shoulder: [joint1, joint2]
    elbow: [joint3]
    wrist: [joint4, joint5]
```
This lets the RML say `move right shoulder 1 to 1.5` instead of `move joint1 to 1.5`.

Optional fields: `grippers`, `default_orientation`, `orientation_options`.

The pipeline auto-discovers YAML files in this folder, so no code changes are needed.

## 2. MoveIt config package (required)

Create a MoveIt config package at `ros_ws/src/robots/<robot>_ws/src/<robot>_moveit_config/`.

The package name must be `<robot>_moveit_config` where `<robot>` matches the YAML filename.

It needs:
- `config/<Robot>.urdf` — robot description
- `config/<Robot>.srdf` — semantic description (planning groups, etc.)
- `config/kinematics.yaml` — IK solver config
- `launch/move_group.launch.py` — launches the MoveIt move_group node

The easiest way is to use the MoveIt Setup Assistant to generate this from a URDF.

## 3. GUI dropdown

Add the robot key to the dropdown in `ros_ws/src/my_qt_gui/ui/main_window.ui`:

Can be done with QT Designer or

```xml
<item>
  <property name="text">
    <string>myrobot</string>
  </property>
</item>
```

## 4. Webots simulation (optional)

If you want to simulate the robot in Webots:

1. Create a world file at `webots/worlds/myrobot.wbt`
2. Create a joint mapping at `webots/controllers/robot_controller/configs/myrobot.yaml` that maps abstract joint names to Webots motor/sensor names
3. Set `robot: myrobot` in `webots/controllers/robot_controller/config.yaml`

## 5. Build and test

```bash
cd ros_ws && colcon build && source install/setup.bash
ros2 launch motion_pipeline_bringup pipeline.launch.py
```

Select your robot in the GUI dropdown.