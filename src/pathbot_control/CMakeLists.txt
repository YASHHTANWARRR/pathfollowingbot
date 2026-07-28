cmake_minimum_required(VERSION 3.8)
project(pathbot_control)

find_package(ament_cmake REQUIRED)

install(
  PROGRAMS
    scripts/path_planner.py
    scripts/pure_pursuit.py
    scripts/publish_path.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch docs
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
