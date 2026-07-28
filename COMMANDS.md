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

## 3. Two bringup modes: mapping vs localization

`bringup.launch.py` runs **either** slam_toolbox **or** AMCL — never both, since
they would fight over the `map -> odom` transform.

| Mode | Command | What runs |
|------|---------|-----------|
| AMCL localization (**default**) | `ros2 launch pathbot_bringup bringup.launch.py` | `map_server` + `amcl` against the saved map |
| SLAM mapping | `ros2 launch pathbot_bringup bringup.launch.py slam:=True` | `slam_toolbox` building a new map |

Use a different map:

```bash
ros2 launch pathbot_bringup bringup.launch.py map:=/absolute/path/to/other.yaml
```

> `slam:=True` / `slam:=False` must be **capitalized** — nav2_bringup evaluates
> it as a Python expression, so `true` raises `NameError: name 'true' is not defined`.

## 4. Making a new map

```bash
# 1. mapping mode
ros2 launch pathbot_bringup bringup.launch.py slam:=True

# 2. drive around (second terminal)
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 3. save it (third terminal, while step 1 still runs)
ros2 run nav2_map_server map_saver_cli \
  -f ~/Desktop/pathfollowingbot/src/pathbot_navigation/maps/warehouse

# 4. rebuild so the map installs into share/
colcon build --packages-select pathbot_navigation && source install/setup.bash
```

Drive **slowly and revisit places** — map quality directly determines how well
AMCL localizes afterwards. Cover the walls (drive the perimeter), and return
along paths you have already taken so slam_toolbox gets loop closures.

## 4b. Odometry calibration (only if you change the wheels/chassis)

This robot is a 4-wheel **skid-steer** driven by a differential-drive plugin.
Its wheels scrub sideways when turning, so odometry over-reports rotation
unless `wheel_separation` is inflated above the geometric track. That factor is
`track_correction` in `pathbot_description/urdf/robot.gazebo.xacro`
(currently **1.91**, i.e. an effective track of 1.34 m vs the geometric 0.70 m).

To re-measure it, launch the sim, then compare `/odom` yaw against Gazebo truth
over a rotation short enough not to wrap past ±π:

```bash
# truth
gz model -m robo_robot -p
# odom (quaternion; yaw = 2*atan2(qz, qw))
ros2 topic echo /odom --field pose.pose.orientation --once

timeout 4 ros2 topic pub -r 50 /cmd_vel geometry_msgs/msg/Twist "{angular: {z: 0.3}}"
```

Then `track_correction_new = track_correction_old × (Δyaw_odom / Δyaw_truth)`.
Rebuild, and repeat until the ratio is within ~5% of 1.0. Measure each
direction from a **fresh** launch — running trials back-to-back contaminates
the result. Re-calibrating invalidates any saved map; re-map afterwards.

Current measured accuracy: rotation 1.7–2.1% error, straight line 2.7%.

## 5. Individual pieces (SLAM / Nav2 standalone)

```bash
ros2 launch pathbot_navigation slam.launch.py
ros2 launch pathbot_navigation nav2.launch.py            # AMCL
ros2 launch pathbot_navigation nav2.launch.py slam:=True # no AMCL
```

## 6. Obstacle stopping (collision monitor)

The robot only avoids obstacles **when Nav2 is driving it**. The nav2 velocity
chain is:

```
controller_server -> /cmd_vel_nav -> velocity_smoother
                  -> /cmd_vel_smoothed -> collision_monitor -> /cmd_vel -> wheels
```

`collision_monitor` watches `/scan_fixed` and gates that stream: a hard `stop`
zone (a box ~0.35 m beyond the bumper) plus an `approach` zone that slows down.

**Manual teleop is NOT protected.** `teleop_twist_keyboard` and
`ros2 topic pub /cmd_vel` publish directly onto `/cmd_vel`, which is the
*output* of the chain — they bypass the monitor entirely and will happily drive
into a wall. To get gating while driving by hand, publish to the chain's input
instead:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r /cmd_vel:=/cmd_vel_smoothed
```

Watch it working:

```bash
ros2 topic echo /collision_monitor_state
ros2 topic echo /collision_monitor_stop_zone   # visualize in RViz
```

## 7. Checking AMCL

```bash
ros2 lifecycle get /amcl          # active [3]
ros2 lifecycle get /map_server    # active [3]
ros2 topic echo /amcl_pose --once
ros2 run tf2_ros tf2_echo map odom
```

AMCL auto-seeds its initial pose at `(0, 0)` (the robot's spawn point, set via
`set_initial_pose` in `nav2_params.yaml`). To re-seed it manually, use RViz's
**2D Pose Estimate** button.

## 8. Path following (Pure Pursuit)

```bash
ros2 launch pathbot_control path_follower.launch.py
```

With custom params:

```bash
ros2 launch pathbot_control path_follower.launch.py lookahead_dist:=1.5 max_speed:=0.3
```

## 9. RViz visualization

```bash
ros2 launch pathbot_description rviz.launch.py
```

## 10. Spawn robot directly (into an already-running world)

```bash
ros2 launch pathbot_simulation spawn_in_track.launch.py
```

## 11. Manual teleop / testing

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

## 12. Inspecting topics / nodes while running

```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic echo /odom
ros2 topic hz /scan
ros2 node list
ros2 run rqt_graph rqt_graph
```

## 13. Publish a path manually (for testing pure pursuit)

```bash
ros2 run pathbot_control publish_path.py
```

## 14. Process management (PIDs)

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

## Typical test session (map -> save -> localize)

```bash
# --- terminal 1: map the world ---
ros2 launch pathbot_bringup bringup.launch.py slam:=True

# --- terminal 2: drive around slowly, revisiting places ---
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# --- terminal 3: save the map, then rebuild ---
ros2 run nav2_map_server map_saver_cli \
  -f ~/Desktop/pathfollowingbot/src/pathbot_navigation/maps/warehouse
colcon build --packages-select pathbot_navigation && source install/setup.bash

# --- stop terminal 1, then relaunch in AMCL mode (the default) ---
ros2 launch pathbot_bringup bringup.launch.py

# --- send a navigation goal from RViz with "2D Goal Pose" ---
```
