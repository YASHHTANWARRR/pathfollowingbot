import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    slam_params = os.path.join(
        get_package_share_directory('mobile_robot'),
        'parameters',
        'mapper_params_online_async.yaml'
    )

    scan_frame_corrector = Node(
        package='mobile_robot',
        executable='scan_frame_corrector',
        output='screen'
    )

    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params,
            {'use_sim_time': True}
        ]
    )

    ld = LaunchDescription()

    ld.add_action(scan_frame_corrector)
    ld.add_action(slam_toolbox)

    return ld