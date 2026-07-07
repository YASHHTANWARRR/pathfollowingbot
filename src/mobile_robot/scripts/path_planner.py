import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np
import heapq

GRID_SIZE = 200
RESOLUTION = 0.05

class Planner(Node):

    def __init__(self):
        super().__init__('planner')

        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10)

        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.grid = np.zeros((GRID_SIZE, GRID_SIZE))

        self.goal = (150, 150)

    def scan_callback(self, msg):
        self.grid.fill(0)

        angle = msg.angle_min
        for r in msg.ranges:
            if r < msg.range_max:
                x = r * np.cos(angle)
                y = r * np.sin(angle)

                gx = int(x / RESOLUTION + GRID_SIZE//2)
                gy = int(y / RESOLUTION + GRID_SIZE//2)

                if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
                    self.grid[gx, gy] = 1

            angle += msg.angle_increment

        path = self.a_star((100,100), self.goal)
        if path:
            self.follow_path(path)

    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for dx in [-1,0,1]:
                for dy in [-1,0,1]:
                    neighbor = (current[0]+dx, current[1]+dy)
                    if 0 <= neighbor[0] < GRID_SIZE and 0 <= neighbor[1] < GRID_SIZE:
                        if self.grid[neighbor] == 1:
                            continue
                        tentative = g_score[current] + 1
                        if neighbor not in g_score or tentative < g_score[neighbor]:
                            g_score[neighbor] = tentative
                            f = tentative + np.linalg.norm(np.array(neighbor)-np.array(goal))
                            heapq.heappush(open_set, (f, neighbor))
                            came_from[neighbor] = current
        return None

    def follow_path(self, path):
        target = path[min(5, len(path)-1)]

        twist = Twist()
        twist.linear.x = 0.2
        twist.angular.z = (target[1]-100) * 0.01
        self.pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = Planner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
