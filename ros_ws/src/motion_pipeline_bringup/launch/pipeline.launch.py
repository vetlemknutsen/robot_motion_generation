from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    moveit_share = get_package_share_directory("tiago_moveit_config")
    move_group_launch = os.path.join(moveit_share, "launch", "move_group.launch.py")

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(move_group_launch),
        ),
        Node(
            package="motion_pipeline_bridge",
            executable="generator_node",
            name="motion_pipeline_generator",
            output="screen",
        ),
        Node(
            package="my_qt_gui",
            executable="my_qt_gui_node",
            name="my_qt_gui",
            output="screen",
        ),
    ])
