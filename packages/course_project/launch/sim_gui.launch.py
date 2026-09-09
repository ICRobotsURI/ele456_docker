#!/usr/bin/env python3
# =============================================================================
# Launch file: Gazebo Harmonic (WITH GUI) + simple diff-drive robot + rviz2
# Use this to demonstrate the Gazebo GUI to students.
# NOTE: Performance will be poor without a GPU.
# =============================================================================

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    SetEnvironmentVariable,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import (
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node


def generate_launch_description():

    # ----- Package directories -----
    pkg_course_project = get_package_share_directory('course_project')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    # ----- Launch arguments -----
    world_arg = DeclareLaunchArgument(
        'world', default_value='world_1',
        description='Name of the world file (without .sdf extension)')

    rviz_arg = DeclareLaunchArgument(
        'rviz', default_value='false',
        choices=['true', 'false'],
        description='Launch rviz2')

    x_arg = DeclareLaunchArgument('x', default_value='0.0')
    y_arg = DeclareLaunchArgument('y', default_value='0.0')

    # ----- Set Gazebo plugin paths (ROS vendor packages) -----
    gz_plugin_path = SetEnvironmentVariable(
        name='GZ_SIM_SYSTEM_PLUGIN_PATH',
        value=':'.join([
            '/opt/ros/jazzy/opt/gz_sim_vendor/lib/gz-sim-8/plugins',
            '/opt/ros/jazzy/opt/gz_sim_vendor/lib',
        ])
    )

    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=':'.join([
            os.path.join(pkg_course_project, 'worlds'),
        ])
    )

    # ----- Gazebo Sim (WITH GUI) -----
    gz_sim_launch = PathJoinSubstitution(
        [pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])

    world_file = PathJoinSubstitution(
        [pkg_course_project, 'worlds', LaunchConfiguration('world')])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_sim_launch]),
        launch_arguments=[
            ('gz_args', [
                world_file,
                '.sdf',
                ' -r',   # Start running immediately
                ' -v 4',
            ])
        ]
    )

    # ----- Robot description -----
    robot_urdf = os.path.join(pkg_course_project, 'models', 'simple_robot.urdf')
    with open(robot_urdf, 'r') as f:
        robot_description = f.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
        output='screen',
    )

    # ----- Spawn robot in Gazebo -----
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'simple_robot',
            '-topic', 'robot_description',
            '-x', LaunchConfiguration('x'),
            '-y', LaunchConfiguration('y'),
            '-z', '0.0',
        ],
        output='screen',
    )

    # ----- ROS-Gazebo bridges -----
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='ros_gz_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
        ],
        parameters=[{'use_sim_time': True}],
    )

    # ----- Fix lidar frame_id -----
    lidar_frame_relay = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='lidar_frame_fix',
        arguments=['0', '0', '0', '0', '0', '0',
                   'lidar_link',
                   'simple_robot/base_footprint/lidar'],
        parameters=[{'use_sim_time': True}],
    )

    # ----- rviz2 (optional) -----
    rviz_config = os.path.join(pkg_course_project, 'config', 'rviz_config.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    # ----- Build launch description -----
    ld = LaunchDescription()

    ld.add_action(world_arg)
    ld.add_action(rviz_arg)
    ld.add_action(x_arg)
    ld.add_action(y_arg)

    ld.add_action(gz_plugin_path)
    ld.add_action(gz_resource_path)

    ld.add_action(gazebo)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_robot)
    ld.add_action(bridge)
    ld.add_action(lidar_frame_relay)
    ld.add_action(rviz)

    return ld
