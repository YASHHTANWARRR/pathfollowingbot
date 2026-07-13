import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mobile_robot'),
                'launch',
                'gazebo_model.launch.py'
            )
        )
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mobile_robot'),
                'launch',
                'slam.launch.py'
            )
        )
    )

    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mobile_robot'),
                'launch',
                'rviz.launch.py'
            )
        )
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mobile_robot'),
                'launch',
                'nav2.launch.py'
            )
        )
    )

    ld = LaunchDescription()

    ld.add_action(gazebo)
    ld.add_action(TimerAction(period=5.0, actions=[slam]))
    ld.add_action(TimerAction(period=8.0, actions=[nav2]))
    ld.add_action(rviz)

    return ld