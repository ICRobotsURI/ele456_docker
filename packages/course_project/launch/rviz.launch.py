#!/usr/bin/env python3
# =============================================================================
# Launch file: rviz2 with pre-configured display (lidar, robot, cylinders)
# Run this alongside the simulation to visualize sensor data.
# =============================================================================

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    pkg_course_project = get_package_share_directory('course_project')
    rviz_config = os.path.join(pkg_course_project, 'config', 'rviz_config.rviz')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([rviz])
