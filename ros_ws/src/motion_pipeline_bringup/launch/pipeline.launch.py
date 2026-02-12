from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="motion_pipeline_bridge",
            executable="generator_node",
            output="screen",
            emulate_tty=True,
            additional_env={"PYTHONUNBUFFERED": "1"},
        )
        ,
        Node(
            package="my_qt_gui",
            executable="my_qt_gui_node",
            name="my_qt_gui",
            output="screen",
        ),
    ])
