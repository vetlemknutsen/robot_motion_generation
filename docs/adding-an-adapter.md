# Adding a New Input Adapter

An adapter converts an input file into a `TaskDescription` (robot-independent task-space steps).

## 1. Create the adapter

Create a new file in:

`motion_pipeline/motion_pipeline/adapters/`

Example:

```python
from pathlib import Path
from motion_pipeline.adapters.base import Adapter, register_adapter
from motion_pipeline.types.TaskDescription import TaskDescription

@register_adapter("myadapter")
class MyAdapter(Adapter):
    def to_taskdescription(self, source: Path) -> TaskDescription:
        # parse file and return TaskDescription
        ...
```

Notes:
- Adapter keys should be lowercase (GUI sends adapter names in lowercase).
- Implement `to_taskdescription(...)`

## 2. Make sure it is imported

Add your adapter import in:

`motion_pipeline/motion_pipeline/adapters/__init__.py`

Example:

```python
from motion_pipeline.adapters import my_adapter
```

This is needed because the pipeline imports `motion_pipeline.adapters` to populate the adapter registry.

## 3. Add it to GUI dropdown

Edit:

`ros_ws/src/qt_gui/ui/main_window.ui`

Add item to `adapterBox` (via Qt Designer or XML). Example label:

```xml
<string>MyAdapter</string>
```

## 4. Rebuild and test

```bash
colcon build
source install/setup.bash
```

Then select the adapter in GUI and generate.

## Existing adapters

- `simple_json_adapter.py` (key: `json`)
- `mediapipe_csv_adapter.py` (key: `mediapipecsv`)
