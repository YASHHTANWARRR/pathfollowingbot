# 🚗 Path Following Robot using ROS 2 Jazzy & Gazebo Sim

A complete simulation package for a **4-wheel differential drive mobile robot** built using **ROS 2 Jazzy** and **Gazebo Sim (Ignition Gazebo)**. The robot is equipped with a **360° GPU LiDAR** and is designed for autonomous navigation research including **SLAM**, **Navigation2**, **Path Planning**, and **Path Following**.

---

## 📌 Features

- 🚗 4-Wheel Differential Drive Robot
- 📡 360° GPU LiDAR
- 🦾 URDF/Xacro Robot Model
- 🏭 AWS RoboMaker Small Warehouse World
- ⚙️ ROS 2 Jazzy Compatible
- 🧩 Multi-package workspace (bringup / simulation / description / navigation / control / nodes)
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

The workspace is split into focused ROS 2 packages under `src/`:

```text
src/
│
├── pathbot_bringup/          # Top-level launch that starts everything together
│   └── launch/
│       └── bringup.launch.py
│
├── pathbot_simulation/       # Gazebo world, warehouse models, robot spawning
│   ├── launch/
│   │   ├── gazebo_model.launch.py
│   │   └── spawn_in_track.launch.py
│   ├── worlds/
│   │   └── small_warehouse.world
│   ├── models/                 # AWS RoboMaker warehouse assets
│   └── config/
│       └── bridge_parameters.yaml
│
├── pathbot_description/      # Robot URDF/Xacro model + RViz viewing
│   ├── urdf/
│   │   ├── robot.xacro
│   │   └── robot.gazebo.xacro
│   ├── rviz/
│   │   └── slam.rviz
│   └── launch/
│       └── rviz.launch.py
│
├── pathbot_navigation/       # SLAM, Nav2, map saving
│   ├── launch/
│   │   ├── slam.launch.py
│   │   ├── nav2.launch.py
│   │   └── map_saver.launch.py
│   ├── config/
│   │   ├── slam_toolbox.yaml
│   │   └── nav2_params.yaml
│   └── maps/
│
├── pathbot_control/          # Pure pursuit path following
│   ├── scripts/
│   │   ├── pure_pursuit.py
│   │   ├── publish_path.py
│   │   └── path_planner.py
│   └── launch/
│       └── path_follower.launch.py
│
└── pathbot_nodes/            # Custom C++ nodes
    └── src/
        └── scan_frame_corrector.cpp
```

Each package has its own `package.xml` and `CMakeLists.txt`. See [COMMANDS.md](COMMANDS.md) for the full command reference.

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

Build (all packages)

```bash
cd ~/Desktop/pathfollowingbot

colcon build --symlink-install
```

Build a single package

```bash
colcon build --packages-select pathbot_simulation
```

Source

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

---

# ▶️ Launch Simulation

```bash
ros2 launch pathbot_simulation gazebo_model.launch.py
```

The launch file starts

- Gazebo Sim (AWS RoboMaker small warehouse world)
- Robot State Publisher
- Robot Spawn
- Gazebo Plugins
- LiDAR Sensor
- ROS-Gazebo Bridge

Or launch everything together (Gazebo + SLAM + Nav2 + RViz):

```bash
ros2 launch pathbot_bringup bringup.launch.py
```

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

<img width="1877" height="1072" alt="image" src="https://github.com/user-attachments/assets/0c65a87f-98ac-4584-beab-3968bf1526b8" />


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

Launch SLAM

```bash
ros2 launch pathbot_navigation slam.launch.py
```

Visualize in RViz

```bash
ros2 launch pathbot_description rviz.launch.py
```

Save generated map

```bash
ros2 launch pathbot_navigation map_saver.launch.py
```

---

# 🧭 Navigation2

After generating the map, launch Navigation2.

```bash
ros2 launch pathbot_navigation nav2.launch.py
```

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

# 🚙 Path Following

Launch the pure pursuit controller (with the path publisher):

```bash
ros2 launch pathbot_control path_follower.launch.py
```

With custom parameters:

```bash
ros2 launch pathbot_control path_follower.launch.py lookahead_dist:=1.5 max_speed:=0.3
```

Also compatible with

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
