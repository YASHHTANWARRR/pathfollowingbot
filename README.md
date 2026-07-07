# Path Following Robot using ROS 2 Jazzy & Gazebo Sim

A ROS 2 Jazzy package for simulating a **4-wheel differential drive mobile robot** equipped with a **2D GPU LiDAR** in **Gazebo Sim (Ignition Gazebo)**. This project provides a complete simulation environment for developing and testing autonomous navigation, path planning, and path following algorithms.

---

## Features

- 🚗 4-Wheel Differential Drive Robot
- 📡 GPU LiDAR Sensor
- 🦾 URDF/Xacro Robot Model
- 🌍 Custom Gazebo Simulation World
- ⚙️ ROS 2 Jazzy Compatible
- 🛰️ Odometry Generation
- 🔄 Joint State Publishing
- 🎮 Velocity Control using `/cmd_vel`
- 📈 Ready for SLAM Toolbox & Nav2 Integration

---

## Robot Configuration

| Component | Description |
|-----------|-------------|
| Drive Type | Differential Drive |
| Wheels | Four Wheels |
| Sensor | GPU LiDAR |
| Simulation | Gazebo Sim 8 |
| ROS Version | ROS 2 Jazzy |

---

# Project Structure

```text
mobile_robot/
├── config/
├── launch/
│   └── gazebo_model.launch.py
├── model/
│   ├── robot.urdf.xacro
│   ├── robot.gazebo.xacro
│   └── materials/
├── meshes/
├── maps/
├── worlds/
│   └── track.world
├── rviz/
├── package.xml
└── CMakeLists.txt
```

---

# Dependencies

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Sim 8
- ros_gz
- Xacro

Install dependencies

```bash
sudo apt update

sudo apt install \
ros-jazzy-desktop \
ros-jazzy-ros-gz \
ros-jazzy-xacro \
ros-jazzy-joint-state-publisher \
ros-jazzy-robot-state-publisher
```

---

# Build

Clone into your workspace

```bash
cd ~/Desktop/pathfollowingbot/src
```

Build

```bash
cd ~/Desktop/pathfollowingbot
colcon build --symlink-install
```

Source

```bash
source install/setup.bash
```

---

# Launch Simulation

```bash
ros2 launch mobile_robot gazebo_model.launch.py
```

This launches

- Gazebo Sim
- Robot State Publisher
- Robot Spawn
- Robot Model

---

# Robot Control

Move Forward

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.5}, angular: {z: 0.0}}" -r 10
```

Rotate

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.5}}" -r 10
```

Stop

```bash
ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.0}}"
```

---

# ROS Topics

| Topic | Type | Description |
|--------|------|-------------|
| `/cmd_vel` | geometry_msgs/Twist | Velocity Commands |
| `/odom` | nav_msgs/Odometry | Robot Odometry |
| `/scan` | sensor_msgs/LaserScan | LiDAR Data |
| `/joint_states` | sensor_msgs/JointState | Joint States |
| `/tf` | tf2_msgs/TFMessage | Robot Transform Tree |
| `/clock` | rosgraph_msgs/Clock | Simulation Clock |

---

# TF Tree

```
odom
└── body_footprint
    └── body_link
        ├── wheel_front_left
        ├── wheel_front_right
        ├── wheel_rear_left
        ├── wheel_rear_right
        └── lidar_link
```

---

# Robot Plugins

### Differential Drive Plugin

Provides

- Wheel control
- Odometry publishing
- TF publishing
- Velocity commands

---

### Joint State Publisher

Publishes

```
/joint_states
```

---

### GPU LiDAR

Publishes

```
/scan
```

Used for

- Mapping
- Localization
- Navigation
- Obstacle Detection

---

# Visualization

Launch RViz

```bash
rviz2
```

Recommended Displays

- RobotModel
- LaserScan
- TF
- Odometry
- Map

---

# SLAM

Compatible with

- SLAM Toolbox

Launch

```bash
ros2 launch slam_toolbox online_async_launch.py
```

---

# Navigation

Can be integrated with

- Nav2
- AMCL
- Pure Pursuit
- Stanley Controller
- MPC
- A*
- Dijkstra
- RRT

---

#OUTPUTS
<img width="1587" height="883" alt="Screenshot from 2026-07-07 22-18-26" src="https://github.com/user-attachments/assets/8661dab0-77f8-4e5c-8bef-d5892c12bac6" />

---

---

# Future Improvements

- Stereo Camera
- IMU
- Wheel Encoders
- EKF Localization
- Autonomous Navigation
- Dynamic Obstacle Avoidance
- Waypoint Following
- Path Planning Algorithms
- Occupancy Grid Mapping

---

# Author

**Yash Tanwar**

B.E. Computer Engineering

Thapar Institute of Engineering and Technology

---

# License

This project is licensed under the MIT License.
