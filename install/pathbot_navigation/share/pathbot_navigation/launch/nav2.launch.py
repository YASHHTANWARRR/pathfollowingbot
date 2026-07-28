import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetLaunchConfiguration)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression


def generate_launch_description():

    pkg = get_package_share_directory('pathbot_navigation')

    params_file = os.path.join(pkg, 'config', 'nav2_params.yaml')
    default_map = os.path.join(pkg, 'maps', 'warehouse.yaml')

    # NOTE: nav2_bringup evaluates 'slam' / 'use_localization' as raw Python
    # expressions, so these must be 'True'/'False'. Lowercase 'false' raises
    # NameError: name 'false' is not defined.
    declare_slam = DeclareLaunchArgument(
        'slam',
        default_value='False',
        description="'True' to map with slam_toolbox, 'False' to localize with AMCL"
    )

    declare_map = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Map yaml used by AMCL (ignored when slam:=True)'
    )

    slam = LaunchConfiguration('slam')

    # Resolve "not slam" HERE, into a private name, before the include below.
    # Inside launch_arguments the entries are applied in order, so 'slam' is
    # already overwritten to 'False' by the time a sibling entry is evaluated
    # -- computing use_localization inline would always yield True and start
    # AMCL alongside slam_toolbox, with both fighting over map -> odom.
    set_use_localization = SetLaunchConfiguration(
        'pathbot_use_localization',
        PythonExpression(['not ', slam])
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
            'map': LaunchConfiguration('map'),
            'use_sim_time': 'true',
            'autostart': 'true',
            'use_composition': 'False',
            # We start slam_toolbox ourselves from slam.launch.py, so nav2 must
            # never start its own. 'use_localization' is what selects
            # map_server + AMCL.
            'slam': 'False',
            'use_localization': LaunchConfiguration('pathbot_use_localization'),
        }.items(),
    )

    return LaunchDescription([
        declare_slam,
        declare_map,
        set_use_localization,
        nav2,
    ])
