import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            TimerAction)
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    nav_pkg = get_package_share_directory('pathbot_navigation')

    # NOTE: this is forwarded into nav2_bringup, which evaluates it as a raw
    # Python expression, so it must be 'True'/'False' - not 'true'/'false'.
    declare_slam = DeclareLaunchArgument(
        'slam',
        default_value='False',
        description="'True' to build a map with slam_toolbox, "
                    "'False' to localize with AMCL against a saved map"
    )

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(nav_pkg, 'maps', 'warehouse.yaml'),
        description='Map yaml for AMCL (ignored when slam:=True)'
    )

    slam_arg = LaunchConfiguration('slam')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('pathbot_simulation'),
                'launch',
                'gazebo_model.launch.py'
            )
        )
    )

    # slam_toolbox and AMCL both publish map -> odom, so exactly one may run.
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_pkg, 'launch', 'slam.launch.py')
        ),
        condition=IfCondition(slam_arg)
    )

    # AMCL subscribes to /scan_fixed, so this must run in localization mode
    # too. In slam mode slam.launch.py already starts it, hence the inverse
    # condition here - exactly one copy runs either way.
    scan_frame_corrector = Node(
        package='pathbot_nodes',
        executable='scan_frame_corrector',
        parameters=[{'use_sim_time': True}],
        output='screen',
        condition=UnlessCondition(slam_arg),
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
            os.path.join(nav_pkg, 'launch', 'nav2.launch.py')
        ),
        launch_arguments={
            'slam': slam_arg,
            'map': LaunchConfiguration('map'),
        }.items(),
    )

    ld = LaunchDescription()

    # The robot spawns ~6s in (see pathbot_simulation/gazebo_model.launch.py),
    # so SLAM/AMCL must start after that or they come up with no TF/scan.
    ld.add_action(declare_slam)
    ld.add_action(declare_map)
    ld.add_action(gazebo)
    ld.add_action(TimerAction(period=9.0, actions=[scan_frame_corrector, slam]))
    ld.add_action(TimerAction(period=13.0, actions=[nav2]))
    ld.add_action(rviz)

    return ld
