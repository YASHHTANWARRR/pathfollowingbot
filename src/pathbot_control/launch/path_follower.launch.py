import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    ld.add_action(DeclareLaunchArgument('lookahead_dist', default_value='1.0'))
    ld.add_action(DeclareLaunchArgument('max_speed', default_value='0.5'))

    pure_pursuit_node = Node(
        package='pathbot_control',
        executable='pure_pursuit.py',
        parameters=[{
            'lookahead_dist': LaunchConfiguration('lookahead_dist'),
            'max_linear_speed': LaunchConfiguration('max_speed'),
            'use_sim_time': True,
        }],
        output='screen',
    )

    path_pub_node = Node(
        package='pathbot_control',
        executable='publish_path.py',
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    ld.add_action(pure_pursuit_node)
    ld.add_action(path_pub_node)

    return ld
