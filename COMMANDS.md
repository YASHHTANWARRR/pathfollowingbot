# Commands Cheat Sheet

Run every command from the workspace root: `/home/hornet/Desktop/pathfollowingbot`

## 0. Setup (once per new shell)

```bash
source /opt/ros/jazzy/setup.bash
source install/setup.bash
```

## 1. Build

```bash
colcon build --packages-select mobile_robot
```

Full rebuild (all packages):

```bash
colcon build
```

## 2. Launch Gazebo + robot (warehouse world)

```bash
ros2 launch mobile_robot gazebo_model.launch.py
```

Or the full bringup (Gazebo + spawn, see [bringup.launch.py](src/mobile_robot/launch/bringup.launch.py)):

```bash
ros2 launch mobile_robot bringup.launch.py
```

## 3. SLAM (build a map)

```bash
ros2 launch mobile_robot slam.launch.py
```

Save the map once SLAM has mapped enough of the world:

```bash
ros2 launch mobile_robot map_saver.launch.py
```

## 4. Navigation (Nav2)

```bash
ros2 launch mobile_robot nav2.launch.py
```

## 5. Path following (Pure Pursuit)

```bash
ros2 launch mobile_robot path_follower.launch.py
```

With custom params:

```bash
ros2 launch mobile_robot path_follower.launch.py lookahead_dist:=1.5 max_speed:=0.3
```

## 6. RViz visualization

```bash
ros2 launch mobile_robot rviz.launch.py
```

## 7. Spawn robot directly on the track (no warehouse world)

```bash
ros2 launch mobile_robot spawn_in_track.launch.py
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
ros2 run mobile_robot publish_path.py
```

## Typical test session (SLAM -> map -> nav)

```bash
# terminal 1
ros2 launch mobile_robot gazebo_model.launch.py

# terminal 2
ros2 launch mobile_robot slam.launch.py

# terminal 3
ros2 launch mobile_robot rviz.launch.py

# drive around manually, then save the map
ros2 launch mobile_robot map_saver.launch.py

# terminal 4 (after map saved, restart without SLAM)
ros2 launch mobile_robot nav2.launch.py
```
