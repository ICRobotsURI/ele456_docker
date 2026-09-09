"""
Grader for World 1
==================
Monitors the robot's position and counts how many cylinders are "visited"
(robot comes within 0.5 m of the cylinder) within 60 seconds.

Usage:
  ros2 run my_package grader_w1

The grader starts timing when the first /cmd_vel message is received.
"""

import rclpy
import math
import numpy as np

from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Twist


class GraderW1(Node):

    # Cylinder positions for world_1 (seed=42, 60 cylinders, 20x20m area)
    CYLINDERS = np.array([
        [2.65, -4.27, 4.49, 7.45, -1.48, -5.35, -9.0, 2.85, -5.31, 5.88,
         5.81, -3.04, 8.69, -7.74, 6.6, 5.84, 0.69, -2.31, 6.87, 3.89,
         -5.17, -7.98, -7.58, 2.58, -2.47, -4.43, 2.81, -6.25, -6.4, 9.3,
         1.08, 6.51, -5.15, -3.51, -5.49, 7.15, 2.95, 7.88, 1.17, 1.61,
         -1.91, 9.45, -7.77, -7.42, 5.55, -8.29, 8.95, -9.28, 3.45, -4.43,
         -7.38, -0.88, 7.14, 0.01, 7.84, -3.83, 2.07, 4.99, -9.49, -9.13],
        [-9.02, -5.26, 3.36, -7.85, -8.93, 0.1, -5.72, 0.85, 1.7, -9.38,
         3.76, -6.55, -3.1, -7.66, 1.97, 4.36, 8.99, 0.99, 1.47, -8.63,
         -4.0, -5.08, -4.22, -2.57, -5.52, 8.3, 2.07, 4.35, -2.29, 2.66,
         3.51, 5.24, -8.89, -4.41, 8.42, -3.52, -1.98, -0.78, -4.51, 7.56,
         -5.33, 0.18, -8.6, 2.42, -1.48, -2.25, 6.85, 4.19, 0.7, 2.68,
         -1.24, 8.62, -4.5, -6.11, 7.04, 2.64, -6.6, 0.75, -3.34, 8.15]
    ])

    TIME_LIMIT = 60  # seconds
    VISIT_RADIUS = 0.5  # meters

    def __init__(self):
        super().__init__('grader_w1')
        self.n = self.CYLINDERS.shape[1]
        self.visited = np.zeros(self.n, dtype=int)
        self.started = False
        self.ended = False
        self.start_time = 0.0

        self.cmdvel_sub = self.create_subscription(
            Twist, '/cmd_vel', self.cmdvel_callback, 1)
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 1)

        self.get_logger().info('Grader W1 ready. Waiting for robot to start moving...')

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

        # Record start time on first odom after start
        if self.start_time == 0.0:
            self.start_time = current_time

        elapsed = current_time - self.start_time

        # Check if time is up
        if elapsed > self.TIME_LIMIT:
            self.ended = True
            score = int(np.sum(self.visited))
            self.get_logger().info('=' * 50)
            self.get_logger().info(f'TIME IS UP! Final score: {score}/{self.n} cylinders visited')
            self.get_logger().info('=' * 50)
            return

        # Check proximity to each cylinder
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

        # Print status periodically
        remaining = max(0, self.TIME_LIMIT - int(elapsed))
        score = int(np.sum(self.visited))
        if int(elapsed) % 5 == 0:  # Every 5 seconds
            self.get_logger().info(
                f'Score: {score}/{self.n} | Time remaining: {remaining}s')


def main(args=None):
    rclpy.init(args=args)
    grader = GraderW1()

    try:
        rclpy.spin(grader)
    except KeyboardInterrupt:
        pass

    grader.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
