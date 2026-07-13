#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped
import numpy as np


def generate_oval_path(center=(0, 0), rx=7.5, ry=4.0, n=200, z=0.5):
    poses = []
    t = np.linspace(0, 2 * np.pi, n)
    cx, cy = center
    for theta in t:
        p = PoseStamped()
        p.pose.position.x = cx + rx * np.cos(theta)
        p.pose.position.y = cy + ry * np.sin(theta)
        p.pose.position.z = z
        p.pose.orientation.w = 1.0
        poses.append(p)
    return poses


class PathPublisher(Node):

    def __init__(self):
        super().__init__('path_publisher')
        self.pub = self.create_publisher(Path, '/plan', 10)
        self.timer = self.create_timer(5.0, self.publish_path)

        self.path = Path()
        self.path.header.frame_id = 'odom'
        self.path.poses = generate_oval_path()

        self.get_logger().info('Path publisher started')

    def publish_path(self):
        self.path.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(self.path)
        self.get_logger().info('Published path')


def main(args=None):
    rclpy.init(args=args)
    node = PathPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
