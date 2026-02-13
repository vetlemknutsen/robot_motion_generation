# Adding a New Input Adapter

An adapter converts an input file (any format) into a `Motion` — the pipeline's robot-independent intermediate representation. The pipeline then handles IK and RML generation automatically.

## Steps

### 1. Create the adapter file

Create a new file in `motion_pipeline/motion_pipeline/adapters/`, for example `my_adapter.py`. Subclass `Adapter` from `base.py` and implement the `to_motion()` method to parse your input file and return a `Motion` object. See the existing adapters for reference.

A `Motion` is a list of `Frame`s. Each frame has:
- `targets` — where to move the end-effector(s) (`Target` with side, position, optional orientation)
- `grippers` — whether to open/close grippers (`GripperState` with side, closed)

See `core/task_level.py` for the dataclass definitions.

### 2. Register in generate.py

In `motion_pipeline/motion_pipeline/runtime/generate.py`, add your adapter to the `ADAPTERS` dict:

```python
from motion_pipeline.adapters.my_adapter import MyAdapter

ADAPTERS = {
    "json" : JsonScenarioAdapter,
    "mediapipe_csv" : MediaPipeCSVAdapter,
    ...
    "my_adapter" : MyAdapter,
}
```

### 3. Add to the GUI dropdown

In `ros_ws/src/my_qt_gui/ui/main_window.ui`, add an item to the `adapterBox`:

Can be done with QT Designer or

```xml
<item>
  <property name="text">
    <string>my_adapter</string>
  </property>
</item>
```

### 4. Rebuild and test

```bash
cd ros_ws && colcon build && source install/setup.bash
```

Then select your adapter in the GUI and run with an input file.

## Existing adapters for reference

- `symbolic_json_adapter.py` — parses a simple JSON format with move/gripper actions
- `mediapipe_csv_adapter.py` — parses MediaPipe pose CSV files

## Key types

```
Motion
  └── Frame (one timestep)
        ├── Target (side, position [x,y,z], orientation [x,y,z,w])
        └── GripperState (side, closed)
```