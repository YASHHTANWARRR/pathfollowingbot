import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    map_saver = Node(
        package='nav2_map_server',
        executable='map_saver_server',
        output='screen',
        parameters=[{
            'save_map_timeout': 5.0,
            'free_thresh_default': 0.25,
            'occupied_thresh_default': 0.65,
            'use_sim_time': True,
        }]
    )

    # map_saver_server is a lifecycle node: without this manager it stays
    # "unconfigured" forever and the save_map service never becomes available.
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_map_saver',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_saver'],
        }]
    )

    return LaunchDescription([
        map_saver,
        lifecycle_manager,
    ])
