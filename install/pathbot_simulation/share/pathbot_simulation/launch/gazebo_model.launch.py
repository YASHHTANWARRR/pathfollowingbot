import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, TimerAction,
                            DeclareLaunchArgument)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    # name of the robot defined in the Xacro file
    robotXacroName = 'robo_robot'

    # name of this package and the package holding the robot model
    namePackage = 'pathbot_simulation'
    descriptionPackage = 'pathbot_description'

    # relative path of the xacro file
    modelFileRelativePath = 'urdf/robot.gazebo.xacro'

    # absolute path of the model
    pathModelFile = os.path.join(
        get_package_share_directory(descriptionPackage),
        modelFileRelativePath
    )

    # Nav2's warehouse world. Its props are pulled from Fuel
    # (fuel.gazebosim.org) and cached in ~/.gz/fuel, so the first launch needs
    # an internet connection and takes a while to download.
    pathWorldFile = os.path.join(
        get_package_share_directory('nav2_minimal_tb4_sim'),
        'worlds',
        'warehouse.sdf'
    )

    # get robot description
    robotDescription = xacro.process_file(pathModelFile).toxml()

    # Gazebo launch file
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(
            get_package_share_directory('ros_gz_sim'),
            'launch',
            'gz_sim.launch.py'
        )
    )

    # start Gazebo with the warehouse world
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments={
            'gz_args': f'-r -v 4 {pathWorldFile}',
            'on_exit_shutdown': 'true'
        }.items()
    )

    # spawn robot into Gazebo
    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', robotXacroName,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.5'
        ],
        output='screen',
    )

    # robot state publisher
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[
            {'robot_description': robotDescription},
            {'use_sim_time': True}
        ],
        output='screen',
    )
    # bridge parameters file
    params_file = os.path.join(
        get_package_share_directory(namePackage),
        'config',
        'bridge_parameters.yaml'
    )

    # Gazebo ↔ ROS bridge
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'config_file': params_file}],
        output='screen',
    )


    # launch description
    LaunchDescriptionObject = LaunchDescription()

    LaunchDescriptionObject.add_action(
        DeclareLaunchArgument(
            'spawn_delay',
            default_value='6.0',
            description='Seconds to wait after Gazebo starts before spawning '
                        'the robot.'
        )
    )
    LaunchDescriptionObject.add_action(gazeboLaunch)

    # Give Gazebo time to finish loading the warehouse meshes before spawning,
    # so the robot lands in a fully-initialised world (and its LiDAR attaches).
    # Tune with: spawn_delay:=<seconds>
    LaunchDescriptionObject.add_action(
        TimerAction(
            period=LaunchConfiguration('spawn_delay'),
            actions=[spawnModelNodeGazebo]
        )
    )

    LaunchDescriptionObject.add_action(nodeRobotStatePublisher)
    LaunchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    
    return LaunchDescriptionObject
