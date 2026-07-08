import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    slam_params = os.path.join(
        get_package_share_directory("mobile_robot"),
        "parameters",
        "slam_toolbox.yaml"
    )

    scan_frame_corrector = Node(
        package="mobile_robot",
        executable="scan_frame_corrector",
        output="screen"
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("slam_toolbox"),
                "launch",
                "online_async_launch.py"
            )
        ),
        launch_arguments={
            "slam_params_file": slam_params,
            "use_sim_time": "true",
        }.items(),
    )

    return LaunchDescription([
        scan_frame_corrector,
        slam,
    ])