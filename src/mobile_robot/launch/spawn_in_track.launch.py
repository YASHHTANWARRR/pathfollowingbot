from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from launch.substitutions import Command
from launch_ros.parameter_descriptions import ParameterValue
import os


def generate_launch_description():

    pkg_path = os.path.expanduser(
        '~/autonomous-vehicle-/src/mobile_robot'
    )

    xacro_file = os.path.join(pkg_path, 'model', 'robot.xacro')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]),  # <-- space is important
        value_type=str
    )

    return LaunchDescription([

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description}],
            output='screen'
        ),

        ExecuteProcess(
            cmd=[
                'ros2', 'run', 'ros_gz_sim', 'create',
                '-topic', 'robot_description',
                '-name', 'my_robot',
                '-x', '0',
                '-y', '0',
                '-z', '0.2'
            ],
            output='screen'
        )
    ])
