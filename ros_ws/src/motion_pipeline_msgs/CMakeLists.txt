cmake_minimum_required(VERSION 3.8)
project(motion_pipeline_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/GenerateRequest.srv"
  "srv/SwitchRobot.srv"
  "msg/PipelineLog.msg"
)

ament_package()
