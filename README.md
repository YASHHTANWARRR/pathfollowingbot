# 🚗 Path Following Robot using ROS 2 Jazzy & Gazebo Sim

A complete simulation package for a **4-wheel differential drive mobile robot** built using **ROS 2 Jazzy** and **Gazebo Sim (Ignition Gazebo)**. The robot is equipped with a **360° GPU LiDAR** and is designed for autonomous navigation research including **SLAM**, **Navigation2**, **Path Planning**, and **Path Following**.

---

## 📌 Features

- 🚗 4-Wheel Differential Drive Robot
- 📡 360° GPU LiDAR
- 🦾 URDF/Xacro Robot Model
- 🌍 Custom Gazebo Simulation Environment
- ⚙️ ROS 2 Jazzy Compatible
- 🛰️ Differential Drive Odometry
- 🔄 Joint State Publisher
- 🎮 `/cmd_vel` Velocity Control
- 📈 Ready for SLAM Toolbox
- 🧭 Navigation2 Compatible
- 🛣️ Designed for Autonomous Path Planning & Path Following

---

# 🛠️ Technologies Used

- ROS 2 Jazzy
- Gazebo Sim 8
- URDF
- Xacro
- Gazebo Plugins
- RViz2
- SLAM Toolbox
- Navigation2
- ros_gz_bridge

---

# 📂 Project Structure

```text
mobile_robot/
│
├── launch/
│   ├── gazebo_model.launch.py
│   └── spawn_in_track.launch.py
│
├── model/
│   ├── robot.xacro
│   ├── robot.gazebo.xacro
│   └── materials/
│
├── worlds/
│   └── track.world
│
├── maps/
│
├── rviz/
│
├── images/
│   ├── gazebo_world.png
│   ├── robot_spawn.png
│   ├── lidar_visualization.png
│   ├── rviz_scan.png
│   ├── slam_map.png
│   ├── nav2_navigation.png
│   └── path_following.png
│
├── package.xml
└── CMakeLists.txt
```

---

# 🤖 Robot Specifications

| Parameter | Value |
|------------|-------|
| Drive Type | Differential Drive |
| Wheels | 4 |
| Sensor | 360° GPU LiDAR |
| Simulation | Gazebo Sim 8 |
| ROS Version | ROS 2 Jazzy |
| Robot Model | URDF + Xacro |

---

# ⚙️ Gazebo Plugins

## Differential Drive

Provides

- Wheel Control
- Odometry
- TF
- Velocity Commands

Topics

```
/cmd_vel
/odom
/tf
```

---

## Joint State Publisher

Publishes

```
/joint_states
```

---

## GPU LiDAR

Publishes

```
/scan
```

Provides

- 360° Laser Scan
- Obstacle Detection
- Mapping
- Navigation

---

# 📦 Dependencies

Install ROS 2 Jazzy packages

```bash
sudo apt update

sudo apt install \
ros-jazzy-desktop \
ros-jazzy-ros-gz \
ros-jazzy-xacro \
ros-jazzy-joint-state-publisher \
ros-jazzy-robot-state-publisher \
ros-jazzy-slam-toolbox \
ros-jazzy-navigation2 \
ros-jazzy-nav2-bringup
```

---

# 🔨 Build

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

# ▶️ Launch Simulation

```bash
ros2 launch mobile_robot gazebo_model.launch.py
```

The launch file starts

- Gazebo Sim
- Robot State Publisher
- Robot Spawn
- Gazebo Plugins
- LiDAR Sensor
- ROS-Gazebo Bridge

---

# 🎮 Robot Control

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

# 📡 ROS Topics

| Topic | Type | Description |
|--------|------|-------------|
| `/cmd_vel` | geometry_msgs/Twist | Robot Velocity Commands |
| `/odom` | nav_msgs/Odometry | Robot Odometry |
| `/scan` | sensor_msgs/LaserScan | LiDAR Scan |
| `/joint_states` | sensor_msgs/JointState | Wheel States |
| `/tf` | tf2_msgs/TFMessage | Robot TF Tree |
| `/clock` | rosgraph_msgs/Clock | Simulation Clock |

---

# 🌳 TF Tree

```
odom
└── body_footprint
    └── body_link
        ├── wheel1_link
        ├── wheel2_link
        ├── wheel3_link
        ├── wheel4_link
        └── lidar_link
```

---

# 🖼️ Output

## LiDAR Visualization

360° GPU LiDAR detecting surrounding obstacles.

<img width="1587" height="883" alt="Screenshot from 2026-07-07 22-18-26" src="https://github.com/user-attachments/assets/b7f3707b-3cd0-434a-a9f0-15f0b340f746" />

---

## RViz Visualization

LaserScan visualization in RViz.



---

## SLAM Mapping

Occupancy Grid generated using SLAM Toolbox.


---

## Navigation2

Autonomous navigation using Nav2.

---

## Path Following

Robot following the generated path inside the environment.



---

# 🗺️ SLAM

Launch SLAM Toolbox

```bash
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
```

Save generated map

```bash
ros2 run nav2_map_server map_saver_cli -f my_map
```

---

# 🧭 Navigation2

After generating the map, launch Navigation2.

Features

- AMCL Localization
- Global Planner
- Local Planner
- Recovery Behaviors
- Obstacle Avoidance
- Goal Navigation

---

# 🛣️ Path Planning

The project can be extended with

- A* Search
- Dijkstra
- Theta*
- Hybrid A*
- RRT
- RRT*
- PRM

---

# 🚙 Path Following Controllers

Compatible with

- Pure Pursuit
- Regulated Pure Pursuit
- Stanley Controller
- MPC
- DWB Controller
- TEB Local Planner

---

# 🚀 Future Improvements

- IMU Integration
- Camera Integration
- Stereo Vision
- EKF Localization
- Loop Closure
- Dynamic Obstacle Avoidance
- Multi-Robot Navigation
- Outdoor Navigation
- GPS Integration

---

# 👨‍💻 Author

**Yash Tanwar**

B.E. Computer Engineering

Thapar Institute of Engineering and Technology

---

# ⭐ If you found this project useful, consider giving it a Star!
