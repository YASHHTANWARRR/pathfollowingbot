import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro


def generate_launch_description():

    # name of the robot defined in the Xacro file
    robotXacroName = 'robo_robot'

    # name of the package
    namePackage = 'mobile_robot'

    # relative path of the xacro file
    modelFileRelativePath = 'model/robot.xacro'
    worldFileRelativePath = 'worlds/track.world'

    # absolute path of the model
    pathModelFile = os.path.join(
        get_package_share_directory(namePackage),
        modelFileRelativePath
    )

    pathWorldFile = os.path.join(
        get_package_share_directory(namePackage),
        worldFileRelativePath
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

    # start Gazebo with the path-planning track world
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
            '-x', '-7.0',
            '-y', '-4.0',
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
        get_package_share_directory('mobile_robot'),
        'parameters',
        'bridge_parameters.yaml'
    )   

    # Gazebo ↔ ROS bridge
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
            "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
            "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
        output='screen',
    )


    # launch description
    LaunchDescriptionObject = LaunchDescription()

    LaunchDescriptionObject.add_action(gazeboLaunch)

    # delay spawn so sensors (LiDAR) attach correctly
    LaunchDescriptionObject.add_action(
        TimerAction(
            period=3.0,
            actions=[spawnModelNodeGazebo]
        )
    )

    LaunchDescriptionObject.add_action(nodeRobotStatePublisher)
    LaunchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    
    return LaunchDescriptionObject
