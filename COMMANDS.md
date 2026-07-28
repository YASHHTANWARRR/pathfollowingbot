# Commands Cheat Sheet

Run every command from the workspace root: `/home/hornet/Desktop/pathfollowingbot`

Packages (split out of the old single `mobile_robot` package):

| Package              | Contents                                              |
|----------------------|--------------------------------------------------------|
| `pathbot_bringup`    | Top-level launch that starts everything together        |
| `pathbot_simulation` | Gazebo world, warehouse models, robot spawning          |
| `pathbot_description`| Robot URDF/Xacro model + RViz viewing launch            |
| `pathbot_navigation` | SLAM, Nav2, map saving, maps                            |
| `pathbot_control`    | Pure pursuit path following, path publishing            |
| `pathbot_nodes`      | Custom C++ nodes (e.g. `scan_frame_corrector`)          |

## 0. Setup (once per new shell)

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

## 1. Build

```bash
colcon build
```

Build a single package:

```bash
colcon build --packages-select pathbot_simulation
```

## 2. Launch Gazebo + robot (Nav2 warehouse world)

```bash
ros2 launch pathbot_simulation gazebo_model.launch.py
```

First run downloads the world's props from Gazebo Fuel into `~/.gz/fuel`
(~1–2 min, needs internet). Later runs use the cache.

If the robot spawns before the world finishes loading, increase the delay:

```bash
ros2 launch pathbot_simulation gazebo_model.launch.py spawn_delay:=20.0
```

Or the full bringup (Gazebo + SLAM + Nav2 + RViz, see [bringup.launch.py](src/pathbot_bringup/launch/bringup.launch.py)):

```bash
ros2 launch pathbot_bringup bringup.launch.py
```

## 3. SLAM (build a map)

```bash
ros2 launch pathbot_navigation slam.launch.py
```

Save the map once SLAM has mapped enough of the world:

```bash
ros2 launch pathbot_navigation map_saver.launch.py
```

## 4. Navigation (Nav2)

```bash
ros2 launch pathbot_navigation nav2.launch.py
```

## 5. Path following (Pure Pursuit)

```bash
ros2 launch pathbot_control path_follower.launch.py
```

With custom params:

```bash
ros2 launch pathbot_control path_follower.launch.py lookahead_dist:=1.5 max_speed:=0.3
```

## 6. RViz visualization

```bash
ros2 launch pathbot_description rviz.launch.py
```

## 7. Spawn robot directly on the track (no warehouse world)

```bash
ros2 launch pathbot_simulation spawn_in_track.launch.py
```

## 8. Manual teleop / testing

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 9. Inspecting topics / nodes while running

```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
ros2 topic hz /scan
ros2 node list
ros2 run rqt_graph rqt_graph
```

## 10. Publish a path manually (for testing pure pursuit)

```bash
ros2 run pathbot_control publish_path.py
```

## 11. Process management (PIDs)

Find PIDs for running ROS/Gazebo processes:

```bash
ps aux | grep -E "ros2|gz sim|gazebo"
pgrep -fl "gz sim"
pgrep -fl "ros2 launch"
```

Get the PID of a specific node:

```bash
ros2 node info /slam_toolbox
pgrep -fl slam_toolbox
```

Kill a stuck node/process by PID:

```bash
kill -SIGINT <PID>    # graceful shutdown, try first
kill -SIGTERM <PID>   # if SIGINT doesn't work
kill -9 <PID>         # force kill, last resort
```

Kill everything Gazebo/ROS related if a launch hangs or a window won't close:

```bash
pkill -9 -f "gz sim"
pkill -9 -f "ros2"
pkill -9 -f rviz2
```

Check what's holding a port (e.g. if Gazebo won't start because a previous instance is still running):

```bash
lsof -i :11345
```

## Typical test session (SLAM -> map -> nav)

```bash
# terminal 1
ros2 launch pathbot_simulation gazebo_model.launch.py

# terminal 2
ros2 launch pathbot_navigation slam.launch.py

# terminal 3
ros2 launch pathbot_description rviz.launch.py

# drive around manually, then save the map
ros2 launch pathbot_navigation map_saver.launch.py

# terminal 4 (after map saved, restart without SLAM)
ros2 launch pathbot_navigation nav2.launch.py
```
