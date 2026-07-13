#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import numpy as np


def rounded_rect_path(z=0.5, n_straight=30, n_corner=15):
    pts = []

    def straight(x1, y1, x2, y2, n):
        for i in range(n):
            t = i / n
            p = PoseStamped()
            p.pose.position.x = x1 + t * (x2 - x1)
            p.pose.position.y = y1 + t * (y2 - y1)
            p.pose.position.z = z
            p.pose.orientation.w = 1.0
            pts.append(p)

    def arc(cx, cy, r, a1, a2, n):
        for i in range(n + 1):
            t = i / n
            theta = a1 + t * (a2 - a1)
            p = PoseStamped()
            p.pose.position.x = cx + r * np.cos(theta)
            p.pose.position.y = cy + r * np.sin(theta)
            p.pose.position.z = z
            p.pose.orientation.w = 1.0
            if i > 0:
                pts.append(p)

    straight(-7, -4, 7, -4, n_straight)
    arc(7, -3, 1, -np.pi / 2, 0, n_corner)
    straight(8, -3, 8, 3, n_straight)
    arc(7, 3, 1, 0, np.pi / 2, n_corner)
    straight(7, 4, -7, 4, n_straight)
    arc(-7, 3, 1, np.pi / 2, np.pi, n_corner)
    straight(-8, 3, -8, -3, n_straight)
    arc(-7, -3, 1, np.pi, 3 * np.pi / 2, n_corner)

    return pts


class PathPublisher(Node):

    def __init__(self):
        super().__init__('path_publisher')
        self.pub = self.create_publisher(Path, '/plan', 10)
        self.timer = self.create_timer(5.0, self.publish_path)

        self.path = Path()
        self.path.header.frame_id = 'odom'
        self.path.poses = rounded_rect_path()

        self.get_logger().info('Path publisher started')

    def publish_path(self):
        self.path.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.path)

    # ponytail: publishes every 5s so late-joining nodes get the path


def main(args=None):
    rclpy.init(args=args)
    node = PathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
