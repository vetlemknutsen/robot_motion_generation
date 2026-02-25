cmake_minimum_required(VERSION 3.8)
project(my_qt_gui)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

SET(CMAKE_AUTOMOC ON)
SET(CMAKE_AUTOUIC ON)

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(Qt6 COMPONENTS Widgets REQUIRED)
find_package(std_msgs REQUIRED)
find_package(motion_pipeline_msgs REQUIRED)

add_executable(my_qt_gui_node
  src/main.cpp
  src/main_window.cpp
  include/my_qt_gui/main_window.hpp
  ui/main_window.ui
)

target_include_directories(my_qt_gui_node PRIVATE
  include
)

set_target_properties(my_qt_gui_node PROPERTIES
  AUTOUIC_SEARCH_PATHS "${CMAKE_CURRENT_SOURCE_DIR}/ui")

target_link_libraries(my_qt_gui_node Qt6::Widgets)
ament_target_dependencies(my_qt_gui_node rclcpp std_msgs motion_pipeline_msgs)

install(TARGETS my_qt_gui_node
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY include/
  DESTINATION include)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
