import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
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

    ld = LaunchDescription()

    ld.add_action(gazebo)
    ld.add_action(slam)
    ld.add_action(rviz)

    return ld