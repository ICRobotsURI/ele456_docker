cmake_minimum_required(VERSION 3.8)
project(course_project)

find_package(ament_cmake REQUIRED)

# Install launch files, worlds, models, config, and scripts
install(DIRECTORY launch worlds models config
  DESTINATION share/${PROJECT_NAME}/
)

install(PROGRAMS scripts/publish_markers.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
