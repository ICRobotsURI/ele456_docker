"""
Grader for World 2
==================
Monitors the robot's position and counts how many cylinders are "visited"
(robot comes within 0.5 m of the cylinder) within 60 seconds.

Usage:
  ros2 run my_package grader_w2

The grader starts timing when the first /cmd_vel message is received.
"""

import rclpy
import math
import numpy as np

from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist


class GraderW2(Node):

    # Cylinder positions for world_2 (seed=123, 60 cylinders, 20x20m area)
    CYLINDERS = np.array([
        [-8.51, -1.76, 7.62, 0.69, 6.69, -3.09, -4.84, -1.21, 1.85, -3.51,
         7.7, -6.8, -9.1, 1.39, 6.42, -2.97, -5.57, 0.51, -3.51, 5.12,
         3.51, 3.17, -0.26, -2.38, 4.83, 6.08, 3.0, -8.11, 1.39, -5.91,
         2.44, -2.81, 0.61, 7.77, 9.34, 2.47, -0.31, 9.35, 4.78, -6.94,
         -4.63, -4.33, -8.31, -7.81, -9.34, -8.1, -1.82, -4.51, 4.77, -2.88,
         8.92, -1.54, 3.4, -5.04, 7.2, -6.72, 7.9, 9.02, 2.46, -2.16],
        [-7.84, -7.45, -8.78, -3.19, -6.47, -3.16, -9.47, -7.84, -8.17, -0.98,
         -7.74, 5.51, 7.81, -4.46, 5.11, 5.73, 2.07, 5.88, -1.93, 0.24,
         2.63, 7.41, 3.2, -8.9, -6.05, 7.86, -6.27, -0.82, -3.11, -7.83,
         -9.26, -5.15, 4.25, 2.64, 8.82, -5.07, -6.13, -1.05, -8.66, -5.83,
         -2.81, -1.25, -2.75, -1.27, 0.68, 3.69, 9.22, -0.52, -3.14, 2.64,
         7.29, 4.14, -2.43, -8.01, -8.41, 2.96, 5.25, 0.32, 5.74, -8.32]
    ])

    TIME_LIMIT = 60  # seconds
    VISIT_RADIUS = 0.5  # meters

    def __init__(self):
        super().__init__('grader_w2')
        self.n = self.CYLINDERS.shape[1]
        self.visited = np.zeros(self.n, dtype=int)
        self.started = False
        self.ended = False
        self.start_time = 0.0

        self.cmdvel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmdvel_callback, 1)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 1)

        self.get_logger().info('Grader W2 ready. Waiting for robot to start moving...')

    def cmdvel_callback(self, msg):
        """Detect when the student's node starts publishing commands."""
        if not self.started:
            self.started = True
            self.get_logger().info('Robot started moving! Timer begins now.')

    def odom_callback(self, msg):
        current_time = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        if not self.started:
            self.start_time = current_time
            return

        if self.ended:
            return

        if self.start_time == 0.0:
            self.start_time = current_time

        elapsed = current_time - self.start_time

        if elapsed > self.TIME_LIMIT:
            self.ended = True
            score = int(np.sum(self.visited))
            self.get_logger().info('=' * 50)
            self.get_logger().info(f'TIME IS UP! Final score: {score}/{self.n} cylinders visited')
            self.get_logger().info('=' * 50)
            return

        x = msg.pose.pose.position.x
        y = msg.pose.pose.position.y

        for i in range(self.n):
            if self.visited[i] == 0:
                dist = math.sqrt(
                    (self.CYLINDERS[0, i] - x) ** 2 +
                    (self.CYLINDERS[1, i] - y) ** 2)
                if dist < self.VISIT_RADIUS:
                    self.visited[i] = 1
                    self.get_logger().info(
                        f'Cylinder {i+1} visited! '
                        f'({int(np.sum(self.visited))}/{self.n})')

        remaining = max(0, self.TIME_LIMIT - int(elapsed))
        score = int(np.sum(self.visited))
        if int(elapsed) % 5 == 0:
            self.get_logger().info(
                f'Score: {score}/{self.n} | Time remaining: {remaining}s')


def main(args=None):
    rclpy.init(args=args)
    grader = GraderW2()

    try:
        rclpy.spin(grader)
    except KeyboardInterrupt:
        pass

    grader.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
