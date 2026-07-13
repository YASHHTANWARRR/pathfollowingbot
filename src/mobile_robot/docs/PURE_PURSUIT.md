# Pure Pursuit Path Following Controller

## Overview

A standalone **Pure Pursuit** geometric path tracking controller for differential drive robots. Designed for the `mobile_robot` ROS 2 package, this node follows pre-planned paths by computing curvature-based velocity commands at 20 Hz.

---

## Table of Contents

- [Algorithm](#algorithm)
- [Node Specification](#node-specification)
- [Control Loop Architecture](#control-loop-architecture)
- [Frame Management](#frame-management)
- [Path Publisher (Demo)](#path-publisher-demo)
- [Launch Configuration](#launch-configuration)
- [Usage Workflows](#usage-workflows)
- [Dynamic Reconfiguration](#dynamic-reconfiguration)
- [Integration with Nav2](#integration-with-nav2)
- [ROS Interface Summary](#ros-interface-summary)
- [Troubleshooting](#troubleshooting)

---

## Algorithm

### Pure Pursuit Derivation

The Pure Pursuit controller treats the robot as a point turning with a fixed radius. Given a reference path, it selects a **look-ahead point** at distance `l_d` ahead of the robot and computes the curvature needed to reach it.

#### Geometry

```
                    look-ahead point
                    (t_x, t_y)
                       ★
                      /|
                     / |
                    /  |  l_d
                   /   |
                  / α  |
                 /     |
                /      |
      robot ───────────+
    (p_x, p_y, ψ)     (projected ahead)
```

Where:
- `(p_x, p_y)` — robot position
- `ψ` — robot heading (yaw)
- `(t_x, t_y)` — look-ahead point on the path
- `l_d` — look-ahead distance (Euclidean)
- `α` — angle between robot heading and look-ahead vector

#### Control Law

```
α = atan2(t_y - p_y, t_x - p_x) - ψ
α = atan2(sin(α), cos(α))            # normalize to [-π, π]

κ = 2 · sin(α) / l_d                  # curvature to target

v = v_max / (1.0 + 3.0 · |κ|)        # adaptive speed (slows in curves)
ω = κ · v                             # angular velocity

v = clamp(v, 0, v_max)                # enforce limits
ω = clamp(ω, -ω_max, ω_max)
```

#### Derivation Notes

The curvature `κ = 2·sin(α)/l_d` comes from the intersection of the robot's turning circle with the look-ahead point. For a differential drive robot:

```
R = l_d / (2 · sin(α))                # turning radius
κ = 1 / R = 2 · sin(α) / l_d
```

This is a proportional controller on the heading error `α`, where the gain is `2/l_d`. A larger look-ahead distance reduces gain (smoother, cuts corners). A smaller look-ahead distance increases gain (more responsive, may oscillate).

#### Speed Adaptation

The speed formula `v = v_max / (1 + 3·|κ|)` provides:

| Curvature | Speed Factor | Behavior |
|-----------|-------------|----------|
| `κ = 0` (straight) | `v_max` | Full speed |
| `κ = 0.5` (moderate turn) | `0.4 · v_max` | Reduced speed |
| `κ = 2.0` (sharp turn) | `0.14 · v_max` | Crawl through corners |

---

## Node Specification

### `pure_pursuit.py`

**File**: `scripts/pure_pursuit.py` (188 lines)

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lookahead_dist` | `double` | `1.0` | Look-ahead distance in meters. Higher = smoother paths but cuts corners. Lower = tighter tracking but may oscillate. Recommended range: 0.5–3.0. |
| `max_linear_speed` | `double` | `0.5` | Maximum forward speed in m/s. Actual speed is reduced in curves by the adaptive formula. |
| `max_angular_speed` | `double` | `1.0` | Maximum rotational speed in rad/s. Hard limit, applied after curvature computation. |
| `goal_tolerance` | `double` | `0.3` | Euclidean distance from the final waypoint in meters. When the robot is within this distance, the path is cleared and the robot stops. |
| `control_frequency` | `double` | `20.0` | Control loop rate in Hz. Sets the timer interval for the main control cycle. |
| `robot_frame` | `string` | `body_footprint` | TF frame ID for the robot base. Must match the frame used in the URDF and costmap configuration. |
| `odom_frame` | `string` | `odom` | TF frame ID for odometry. Used to detect when the path is in odom frame for direct pose reading. |

All parameters are dynamically reconfigurable at runtime.

#### Subscriptions

| Topic | Type | QoS | Purpose |
|-------|------|-----|---------|
| `/odom` | `nav_msgs/Odometry` | 10 | Robot pose from Gazebo DiffDrive. Used directly when path is in `odom` frame. |
| `/plan` | `nav_msgs/Path` | 10 | Reference path. The `header.frame_id` is read to determine the coordinate frame. |

#### Publications

| Topic | Type | QoS | Purpose |
|-------|------|-----|---------|
| `/cmd_vel` | `geometry_msgs/Twist` | 10 | Velocity commands to the robot. Only `linear.x` and `angular.z` are set. |

---

## Control Loop Architecture

### Execution Model

The controller uses a `create_timer` with period `1.0 / control_frequency` (50 ms at 20 Hz). This provides:

- **Consistent timing** independent of sensor message rates
- **Decoupled control** — the loop runs even if `/odom` or `/plan` messages arrive late
- **No callback stacking** — each iteration processes the latest available data

### State Machine

```
        ┌───────────────────────────────────────┐
        │                                       │
        ▼                                       │
┌──────────────┐    path received    ┌──────────────────────┐
│    IDLE      │ ──────────────────► │   FOLLOWING          │
│              │                     │                      │
│ no path      │                     │ computing controls   │
│ no cmd_vel   │                     │ publishing /cmd_vel  │
└──────────────┘                     └──────────┬───────────┘
        ▲                                       │
        │                                       │
        │          dist < goal_tolerance        │
        │      ────────────────────────────────►│
        │                                       │
        │   ┌─────────────────────────┐         │
        └───│     GOAL_REACHED        │◄────────┘
            │                         │
            │ path cleared            │
            │ robot stopped           │
            └─────────────────────────┘
```

### Per-Iteration Steps

1. **Guard**: If no path stored, return immediately
2. **Pose acquisition**: Get robot pose via `get_robot_pose()`:
   - If path is in `odom` frame and `/odom` data is available → read directly (O(1))
   - Otherwise → lookup `path_frame → robot_frame` transform via TF2 buffer
   - If pose unavailable → return (try again next cycle)
3. **Closest-point search**: `find_closest_index(px, py)`
   - Search window: `[prev_index - 5, prev_index + 20]`
   - Updates `self.path_index` for temporal coherence
4. **Look-ahead search**: `find_lookahead_index(closest_idx, px, py)`
   - Walks forward from closest index until Euclidean distance ≥ `lookahead_dist`
   - Returns last index if path is shorter than lookahead
5. **Goal check**: If target is the last waypoint and distance < `goal_tolerance` → clear path, stop
6. **Control computation**: `compute_control(px, py, yaw)`
   - Pure Pursuit law → curvature → adaptive speed → clamped twist
7. **Publish**: `cmd_pub.publish(twist)`

---

## Frame Management

### Problem

The robot's pose is available in two frames depending on the system configuration:

| Mode | Path Frame | Robot Pose Source | Frame Match? |
|------|-----------|-------------------|--------------|
| Standalone (publish_path.py) | `odom` | `/odom` topic | ✅ Yes |
| Nav2 integrated | `map` | TF `map → body_footprint` | ❌ No |

### Solution

The `get_robot_pose()` method implements a two-tier fallback:

```python
def get_robot_pose(self):
    # Tier 1: direct odom read (fast path, no TF needed)
    if self.path_frame == self.odom_frame and self.latest_odom:
        return extract_pose_from_odom(self.latest_odom)

    # Tier 2: TF lookup (works across any frames)
    try:
        t = self.tf_buffer.lookup_transform(
            self.path_frame, self.robot_frame, rclpy.time.Time())
        return extract_pose_from_transform(t)
    except Exception:
        return None
```

**Tier 1** (odom-frame path): Reads pose directly from the last `/odom` message. Zero latency, no TF dependency. Used in standalone mode.

**Tier 2** (any frame): Uses `tf2_ros::Buffer` to transform `robot_frame` pose into `path_frame`. Requires the transform chain (e.g., `map → odom → body_footprint`) to be published. Used with Nav2 where `map → odom` comes from AMCL.

---

## Path Publisher (Demo)

### `publish_path.py`

**File**: `scripts/publish_path.py` (59 lines)

Publishes a **rounded-rectangle path** matching the track geometry in `worlds/track.world`. The path is generated from parametric segments:

| Segment | Geometry | Waypoints |
|---------|----------|-----------|
| Bottom straight | y = -4, x: -7 → 7 | 30 |
| Bottom-right corner | Quarter circle, r=1, center (7, -3) | 15 |
| Right straight | x = 8, y: -3 → 3 | 30 |
| Top-right corner | Quarter circle, r=1, center (7, 3) | 15 |
| Top straight | y = 4, x: 7 → -7 | 30 |
| Top-left corner | Quarter circle, r=1, center (-7, 3) | 15 |
| Left straight | x = -8, y: 3 → -3 | 30 |
| Bottom-left corner | Quarter circle, r=1, center (-7, -3) | 15 |

**Total**: 180 waypoints. **Frame**: `odom`.

The path is republished every 5 seconds to accommodate late-joining subscribers. In production use with Nav2, this node is not needed — Nav2's global planner publishes to `/plan` directly.

---

## Launch Configuration

### `path_follower.launch.py`

**File**: `launch/path_follower.launch.py` (35 lines)

Launches both the Pure Pursuit controller and the demo path publisher with configurable parameters.

#### Launch Arguments

| Argument | Default | Passed To |
|----------|---------|-----------|
| `lookahead_dist` | `1.0` | `pure_pursuit.lookahead_dist` |
| `max_speed` | `0.5` | `pure_pursuit.max_linear_speed` |

#### Usage

```bash
# Default parameters
ros2 launch mobile_robot path_follower.launch.py

# Custom parameters
ros2 launch mobile_robot path_follower.launch.py lookahead_dist:=1.5 max_speed:=0.8
```

#### Nodes Launched

| Node | Package | Executable |
|------|---------|------------|
| Pure Pursuit | `mobile_robot` | `pure_pursuit.py` |
| Path Publisher | `mobile_robot` | `publish_path.py` |

---

## Usage Workflows

### Workflow 1: Standalone Path Following

Minimal setup — no SLAM, no Nav2, just Gazebo + path follower.

```bash
# Terminal 1: Launch Gazebo with robot
export GZ_SIM_RESOURCE_PATH=src/mobile_robot/models:$GZ_SIM_RESOURCE_PATH
ros2 launch mobile_robot gazebo_model.launch.py

# Terminal 2: Launch path follower
ros2 launch mobile_robot path_follower.launch.py
```

The robot will autonomously navigate the rounded-rectangle path around the track.

### Workflow 2: Monitor Control Output

```bash
# Watch velocity commands
ros2 topic echo /cmd_vel

# Watch odometry (pose and velocity)
ros2 topic echo /odom

# Check control rate (should be ~20 Hz)
ros2 topic hz /cmd_vel

# Visualize path and robot in RViz
rviz2 -f odom
```

### Workflow 3: Dynamic Parameter Tuning

While the node is running, adjust parameters without restart:

```bash
# Increase look-ahead (smoother but cuts corners)
ros2 param set /pure_pursuit lookahead_dist 2.0

# Decrease look-ahead (tighter tracking)
ros2 param set /pure_pursuit lookahead_dist 0.8

# Increase speed
ros2 param set /pure_pursuit max_linear_speed 0.8

# Decrease speed for safer operation
ros2 param set /pure_pursuit max_linear_speed 0.3
```

### Workflow 4: Custom Path Source

Instead of `publish_path.py`, publish your own path:

```bash
# Publish a simple straight-line path
ros2 topic pub /plan nav_msgs/Path "{
  header: {frame_id: 'odom'},
  poses: [
    {pose: {position: {x: -7.0, y: -4.0, z: 0.5}, orientation: {w: 1.0}}},
    {pose: {position: {x: 7.0, y: -4.0, z: 0.5}, orientation: {w: 1.0}}}
  ]
}" -r 1
```

---

## Dynamic Reconfiguration

The node implements a `set_parameters` callback for runtime reconfiguration:

```python
def param_callback(self, params):
    for p in params:
        if p.name == 'lookahead_dist':
            self.lookahead_dist = p.value
        elif p.name == 'max_linear_speed':
            self.max_v = p.value
        elif p.name == 'max_angular_speed':
            self.max_w = p.value
        elif p.name == 'goal_tolerance':
            self.goal_tol = p.value
    return SetParametersResult(successful=True)
```

This uses ROS 2's standard parameter callback mechanism. Changes take effect on the next control loop iteration (within 50 ms).

---

## Integration with Nav2

The Pure Pursuit controller can replace or supplement Nav2's local planner.

### How It Works with Nav2

1. **Nav2 global planner** publishes a plan to `/plan` in `map` frame
2. **AMCL** publishes `map → odom` transform
3. **Pure Pursuit** uses TF2 to get robot pose in `map` frame
4. Controller computes steering and publishes `/cmd_vel`

### Important Notes

- The `map → odom` transform MUST be published (by AMCL or SLAM Toolbox) for frame-correct operation
- Gazebo's `/cmd_vel` bridge is bi-directional, so the controller can publish directly
- The Nav2 `collision_monitor` and `velocity_smoother` (if configured) will still process the command

### Conflicts

If both Nav2's DWB controller and Pure Pursuit publish to `/cmd_vel`, the last publisher wins. To use Pure Pursuit exclusively, disable Nav2's controller server:

```bash
ros2 lifecycle set /controller_server deactivate
```

---

## ROS Interface Summary

### Topics

| Topic | Direction | Type | Rate |
|-------|-----------|------|------|
| `/cmd_vel` | **Output** | `geometry_msgs/Twist` | 20 Hz |
| `/odom` | **Input** | `nav_msgs/Odometry` | ~50 Hz |
| `/plan` | **Input** | `nav_msgs/Path` | On update |

### Parameters

| Name | Type | Access | Set Command |
|------|------|--------|-------------|
| `lookahead_dist` | `double` | Read/Write | `ros2 param set /pure_pursuit lookahead_dist 1.5` |
| `max_linear_speed` | `double` | Read/Write | `ros2 param set /pure_pursuit max_linear_speed 0.8` |
| `max_angular_speed` | `double` | Read/Write | `ros2 param set /pure_pursuit max_angular_speed 1.5` |
| `goal_tolerance` | `double` | Read/Write | `ros2 param set /pure_pursuit goal_tolerance 0.5` |
| `control_frequency` | `double` | Read-only | — |
| `robot_frame` | `string` | Read-only | — |
| `odom_frame` | `string` | Read-only | — |

---

## Troubleshooting

### No `/cmd_vel` Published

**Symptoms**: `ros2 topic echo /cmd_vel` returns nothing or only zeros.

**Root causes**:

1. **No path received**: The controller stays in IDLE state until `/plan` has data
   ```bash
   ros2 topic echo /plan --once | head -5
   ```

2. **No odometry**: Gazebo must be running and publishing `/odom`
   ```bash
   ros2 topic echo /odom --once | head -5
   ```

3. **TF lookup failure**: When path is in `map` frame but no `map → odom` transform exists
   ```bash
   ros2 run tf2_ros tf2_echo map body_footprint
   ```

### Robot Oscillates on Straight Paths

**Cause**: Look-ahead distance too small relative to speed.

**Fix**: Increase `lookahead_dist` or decrease `max_linear_speed`.

```
# Rule of thumb: lookahead_dist should be ≥ 2× the distance traveled in one control cycle
# At 0.5 m/s and 20 Hz: distance per cycle = 0.025 m → lookahead ≥ 0.05 m (but 0.5–1.0 works better)
```

### Robot Cuts Corners

**Cause**: Look-ahead distance too large — the controller aims ahead around the corner while the robot is still before it.

**Fix**: Decrease `lookahead_dist`. For tight tracks (like this one with 1m corner radii), use 0.8–1.2.

### Robot Drives in Circles

**Cause**: The path frame and robot pose frame don't match. The controller computes a valid steering angle, but in the wrong coordinate frame.

**Diagnosis**: Check the path frame:
```bash
ros2 topic echo /plan --once | grep frame_id
```

**Fixes**:
- If `frame_id: map`: Ensure AMCL or SLAM Toolbox is running (provides `map → odom`)
- If `frame_id: odom`: Ensure robot pose is from `/odom` (not AMCL)
- If `frame_id: ""`: The path publisher didn't set a frame — Pure Pursuit defaults to `odom`

### Intermittent Control (cmd_vel stutters)

**Cause**: TF buffer timeout or intermittent transform availability.

**Diagnosis**: 
```bash
ros2 run tf2_ros tf2_monitor
```

**Fix**: Ensure the transform chain from `path_frame` to `robot_frame` is published at a stable rate.

---

## File Reference

| File | Lines | Role |
|------|-------|------|
| `scripts/pure_pursuit.py` | 188 | Controller implementation |
| `scripts/publish_path.py` | 59 | Demo path publisher |
| `launch/path_follower.launch.py` | 35 | Launch orchestration |
