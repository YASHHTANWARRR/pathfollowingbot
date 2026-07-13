cmake_minimum_required(VERSION 3.8)
project(mobile_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_executable(scan_frame_corrector
  src/scan_frame_corrector.cpp
)

ament_target_dependencies(
  scan_frame_corrector
  rclcpp
  sensor_msgs
)

install(
  TARGETS
    scan_frame_corrector
  DESTINATION lib/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/path_planner.py
    scripts/image_to_world.py
    scripts/track_to_walls.py
    scripts/pure_pursuit.py
    scripts/publish_path.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch model parameters worlds models config maps rviz docs
  DESTINATION share/${PROJECT_NAME}
  PATTERN "build" EXCLUDE
  PATTERN "install" EXCLUDE
  PATTERN "log" EXCLUDE
  PATTERN ".venv" EXCLUDE
)


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
