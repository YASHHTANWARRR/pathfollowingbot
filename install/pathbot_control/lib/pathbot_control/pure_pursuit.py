#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path, Odometry
from geometry_msgs.msg import Twist, PoseStamped
import numpy as np
from rcl_interfaces.msg import SetParametersResult
import tf2_ros


class PurePursuit(Node):

    def __init__(self):
        super().__init__('pure_pursuit')

        self.declare_parameter('lookahead_dist', 1.0)
        self.declare_parameter('max_linear_speed', 0.5)
        self.declare_parameter('max_angular_speed', 1.0)
        self.declare_parameter('goal_tolerance', 0.3)
        self.declare_parameter('control_frequency', 20.0)
        self.declare_parameter('robot_frame', 'body_footprint')
        self.declare_parameter('odom_frame', 'odom')

        self.lookahead_dist = self.get_parameter('lookahead_dist').value
        self.max_v = self.get_parameter('max_linear_speed').value
        self.max_w = self.get_parameter('max_angular_speed').value
        self.goal_tol = self.get_parameter('goal_tolerance').value
        self.robot_frame = self.get_parameter('robot_frame').value
        self.odom_frame = self.get_parameter('odom_frame').value

        self.path = None
        self.path_frame = self.odom_frame
        self.path_index = 0

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.latest_odom = None

        self.path_sub = self.create_subscription(
            Path, '/plan', self.path_callback, 10)

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        dt = 1.0 / self.get_parameter('control_frequency').value
        self.control_timer = self.create_timer(dt, self.control_loop)

        self.add_on_set_parameters_callback(self.param_callback)
        self.get_logger().info('Pure Pursuit node started')

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

    def path_callback(self, msg):
        self.path = msg.poses
        self.path_frame = msg.header.frame_id
        self.path_index = 0
        if self.path_frame == '':
            self.path_frame = 'odom'
        self.get_logger().info(
            f'Received path: {len(self.path)} waypoints in frame {self.path_frame}'
        )

    def odom_callback(self, msg):
        self.latest_odom = msg

    def get_robot_pose(self):
        if self.path_frame == self.odom_frame and self.latest_odom:
            px = self.latest_odom.pose.pose.position.x
            py = self.latest_odom.pose.pose.position.y
            q = self.latest_odom.pose.pose.orientation
            _, _, yaw = self.euler_from_quaternion(q)
            return px, py, yaw
        try:
            t = self.tf_buffer.lookup_transform(
                self.path_frame, self.robot_frame, rclpy.time.Time())
            px = t.transform.translation.x
            py = t.transform.translation.y
            q = t.transform.rotation
            _, _, yaw = self.euler_from_quaternion(q)
            return px, py, yaw
        except Exception:
            return None

    def control_loop(self):
        if self.path is None or len(self.path) == 0:
            return

        pose = self.get_robot_pose()
        if pose is None:
            return

        px, py, yaw = pose
        twist = self.compute_control(px, py, yaw)
        self.cmd_pub.publish(twist)

    def euler_from_quaternion(self, q):
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        return 0.0, 0.0, yaw

    def compute_control(self, px, py, yaw):
        twist = Twist()

        closest_idx = self.find_closest_index(px, py)
        target_idx = self.find_lookahead_index(closest_idx, px, py)

        if target_idx >= len(self.path) - 1:
            dx = self.path[-1].pose.position.x - px
            dy = self.path[-1].pose.position.y - py
            dist = np.hypot(dx, dy)
            if dist < self.goal_tol:
                self.get_logger().info('Goal reached')
                self.path = None
                return twist
            target_idx = len(self.path) - 1

        target = self.path[target_idx].pose.position
        tx, ty = target.x, target.y

        dx = tx - px
        dy = ty - py

        alpha = np.arctan2(dy, dx) - yaw
        alpha = np.arctan2(np.sin(alpha), np.cos(alpha))

        ld = np.hypot(dx, dy)
        if ld < 0.01:
            return twist

        curvature = 2.0 * np.sin(alpha) / ld

        v = self.max_v / (1.0 + 3.0 * abs(curvature))
        w = curvature * v

        v = np.clip(v, 0.0, self.max_v)
        w = np.clip(w, -self.max_w, self.max_w)

        twist.linear.x = v
        twist.angular.z = w
        return twist

    def find_closest_index(self, px, py):
        best_idx = self.path_index
        best_dist = float('inf')
        start = max(0, self.path_index - 5)
        end = min(len(self.path), self.path_index + 20)
        for i in range(start, end):
            dx = self.path[i].pose.position.x - px
            dy = self.path[i].pose.position.y - py
            d = dx * dx + dy * dy
            if d < best_dist:
                best_dist = d
                best_idx = i
        self.path_index = best_idx
        return best_idx

    def find_lookahead_index(self, start_idx, px, py):
        for i in range(start_idx, len(self.path)):
            dx = self.path[i].pose.position.x - px
            dy = self.path[i].pose.position.y - py
            if np.hypot(dx, dy) >= self.lookahead_dist:
                return i
        return len(self.path) - 1


def main(args=None):
    rclpy.init(args=args)
    node = PurePursuit()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
