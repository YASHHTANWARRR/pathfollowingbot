import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pathbot_simulation'),
                'launch',
                'gazebo_model.launch.py'
            )
        )
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pathbot_navigation'),
                'launch',
                'slam.launch.py'
            )
        )
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pathbot_description'),
                'launch',
                'rviz.launch.py'
            )
        )
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pathbot_navigation'),
                'launch',
                'nav2.launch.py'
            )
        )
    )

    ld = LaunchDescription()

    # The robot spawns ~12s in (see pathbot_simulation/gazebo_model.launch.py),
    # so SLAM and Nav2 must start after that or they come up with no TF/scan.
    ld.add_action(gazebo)
    ld.add_action(TimerAction(period=15.0, actions=[slam]))
    ld.add_action(TimerAction(period=20.0, actions=[nav2]))
    ld.add_action(rviz)

    return ld