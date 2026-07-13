import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    params_file = os.path.join(
        get_package_share_directory('mobile_robot'),
        'config',
        'nav2_params.yaml'
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch',
                'bringup_launch.py'
            )
        ),
        launch_arguments={
            'params_file': params_file,
            'use_sim_time': 'true',
            'autostart': 'true',
            'use_composition': 'false',
            'slam': 'False',
            'use_localization': 'False',
        }.items(),
    )

    return LaunchDescription([
        nav2,
    ])
