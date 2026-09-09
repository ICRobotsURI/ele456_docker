"""
Occupancy Grid Mapping Example
==============================

This node subscribes to /scan (LaserScan) and /odom (Odometry) and builds
an occupancy grid map using raycasting. The map is displayed in real-time
using OpenCV.

How it works:
1. We maintain a 2D grid (numpy array) representing the world.
2. Each cell stores a value: 0 = free, 100 = occupied, 50 = unknown.
3. Every time a new laser scan arrives, we:
   a. Get the robot's current position and orientation from odometry.
   b. For each laser ray, we trace from the robot to the endpoint.
   c. Cells along the ray (before the hit) are marked as free.
   d. The cell at the endpoint (where the ray hit something) is marked occupied.
4. We display the grid as an OpenCV image, updated in real-time.

Topics:
  - Subscribes to: /scan (sensor_msgs/LaserScan)
  - Subscribes to: /odom (nav_msgs/Odometry)

Usage:
  ros2 run my_package example_occupancy_grid
"""

import rclpy
import math
import numpy as np
import cv2

from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class OccupancyGridMapper(Node):

    def __init__(self):
        super().__init__('occupancy_grid_mapper')

        # ===================================================================
        # MAP PARAMETERS
        # ===================================================================
        # The map covers a 20m x 20m area centered at the origin (-10 to +10).
        # Each cell is 5cm x 5cm (resolution = 0.05 m/cell).
        # This gives us a 400 x 400 grid.
        # ===================================================================
        self.map_size_m = 20.0          # Total map size in meters
        self.resolution = 0.05          # Meters per cell
        self.grid_size = int(self.map_size_m / self.resolution)  # 400 cells

        # The origin of the map in world coordinates.
        # The map covers from (-10, -10) to (+10, +10).
        self.map_origin_x = -self.map_size_m / 2.0  # -10.0
        self.map_origin_y = -self.map_size_m / 2.0  # -10.0

        # ===================================================================
        # OCCUPANCY GRID
        # ===================================================================
        # We use a log-odds representation internally for numerical stability.
        # log-odds > 0 means more likely occupied
        # log-odds < 0 means more likely free
        # log-odds = 0 means unknown
        # ===================================================================
        self.log_odds_map = np.zeros((self.grid_size, self.grid_size), dtype=np.float64)

        # Log-odds update values (these control how quickly cells become
        # occupied or free). Larger values = faster updates but more noise.
        self.l_occ = 0.85    # log-odds increment for occupied cells
        self.l_free = -0.40  # log-odds increment for free cells

        # Clamp log-odds to prevent extreme values
        self.l_min = -5.0
        self.l_max = 5.0

        # ===================================================================
        # ROBOT STATE (updated from odometry)
        # ===================================================================
        self.robot_x = 0.0
        self.robot_y = 0.0
        self.robot_yaw = 0.0

        # ===================================================================
        # ROS SUBSCRIBERS
        # ===================================================================
        self.odom_sub = self.create_subscription(
            Odometry, '/odom', self.odom_callback, 10)
        self.scan_sub = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        # ===================================================================
        # OPENCV WINDOW
        # ===================================================================
        cv2.namedWindow('Occupancy Grid Map', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Occupancy Grid Map', 800, 800)

        # Timer to refresh the display (5 Hz is enough for visualization)
        self.display_timer = self.create_timer(0.2, self.display_map)

        self.get_logger().info('Occupancy Grid Mapper started.')
        self.get_logger().info(f'Map: {self.grid_size}x{self.grid_size} cells, '
                               f'{self.resolution} m/cell, '
                               f'covers {self.map_size_m}x{self.map_size_m} m')

    # =======================================================================
    # ODOMETRY CALLBACK
    # =======================================================================
    def odom_callback(self, msg):
        """
        Extract the robot's position (x, y) and orientation (yaw) from
        the odometry message. The yaw is computed from the quaternion.
        """
        self.robot_x = msg.pose.pose.position.x
        self.robot_y = msg.pose.pose.position.y

        # Convert quaternion to yaw angle
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.robot_yaw = math.atan2(siny_cosp, cosy_cosp)

    # =======================================================================
    # LASER SCAN CALLBACK
    # =======================================================================
    def scan_callback(self, msg):
        """
        Process each laser ray in the scan:
        1. Compute the world-frame endpoint of the ray.
        2. Use Bresenham's line algorithm to trace cells from robot to endpoint.
        3. Mark cells along the ray as free, and the endpoint cell as occupied.
        """
        angle = msg.angle_min

        for i, distance in enumerate(msg.ranges):
            # Skip invalid readings (inf, nan, or out of range)
            if math.isinf(distance) or math.isnan(distance):
                angle += msg.angle_increment
                continue
            if distance < msg.range_min or distance > msg.range_max:
                angle += msg.angle_increment
                continue

            # -----------------------------------------------------------------
            # Step 1: Compute the endpoint of this ray in world coordinates.
            # The ray starts at the robot's position and goes in the direction
            # of (robot_yaw + ray_angle).
            # -----------------------------------------------------------------
            ray_angle = self.robot_yaw + angle
            end_x = self.robot_x + distance * math.cos(ray_angle)
            end_y = self.robot_y + distance * math.sin(ray_angle)

            # -----------------------------------------------------------------
            # Step 2: Convert world coordinates to grid cell indices.
            # -----------------------------------------------------------------
            robot_cell_x, robot_cell_y = self.world_to_grid(self.robot_x, self.robot_y)
            end_cell_x, end_cell_y = self.world_to_grid(end_x, end_y)

            # -----------------------------------------------------------------
            # Step 3: Trace the ray using Bresenham's algorithm.
            # All cells along the path are FREE (the laser passed through).
            # The final cell is OCCUPIED (the laser hit something).
            # -----------------------------------------------------------------
            ray_cells = self.bresenham(robot_cell_x, robot_cell_y,
                                       end_cell_x, end_cell_y)

            # Mark all cells except the last as free
            for cell in ray_cells[:-1]:
                cx, cy = cell
                if self.is_in_grid(cx, cy):
                    self.log_odds_map[cy, cx] += self.l_free
                    # Clamp
                    self.log_odds_map[cy, cx] = max(self.l_min,
                                                     self.log_odds_map[cy, cx])

            # Mark the last cell (endpoint) as occupied
            if len(ray_cells) > 0:
                cx, cy = ray_cells[-1]
                if self.is_in_grid(cx, cy):
                    self.log_odds_map[cy, cx] += self.l_occ
                    # Clamp
                    self.log_odds_map[cy, cx] = min(self.l_max,
                                                     self.log_odds_map[cy, cx])

            angle += msg.angle_increment

    # =======================================================================
    # HELPER: Convert world coordinates to grid cell indices
    # =======================================================================
    def world_to_grid(self, world_x, world_y):
        """
        Convert a point in world coordinates (meters) to grid cell indices.
        Returns (cell_x, cell_y) as integers.
        """
        cell_x = int((world_x - self.map_origin_x) / self.resolution)
        cell_y = int((world_y - self.map_origin_y) / self.resolution)
        return cell_x, cell_y

    # =======================================================================
    # HELPER: Check if a cell is within the grid bounds
    # =======================================================================
    def is_in_grid(self, cx, cy):
        """Return True if the cell (cx, cy) is within the grid."""
        return 0 <= cx < self.grid_size and 0 <= cy < self.grid_size

    # =======================================================================
    # HELPER: Bresenham's line algorithm
    # =======================================================================
    def bresenham(self, x0, y0, x1, y1):
        """
        Bresenham's line algorithm: returns a list of (x, y) cells
        that form a line from (x0, y0) to (x1, y1).

        This is used to trace the laser ray through the grid.
        It's efficient because it only uses integer arithmetic.
        """
        cells = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            cells.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

        return cells

    # =======================================================================
    # DISPLAY: Convert log-odds map to image and show with OpenCV
    # =======================================================================
    def display_map(self):
        """
        Convert the log-odds occupancy grid to a displayable image:
        - Occupied cells (log-odds > 0) -> black
        - Free cells (log-odds < 0) -> white
        - Unknown cells (log-odds ~= 0) -> gray

        Also draws the robot's position as a small green circle.
        """
        # Convert log-odds to probability: p = 1 - 1/(1 + exp(l))
        # Then map to grayscale: 0 (occupied=black) to 255 (free=white)
        prob_map = 1.0 - 1.0 / (1.0 + np.exp(self.log_odds_map))

        # Scale to 0-255 for display
        # prob=1 means occupied -> display as 0 (black)
        # prob=0 means free -> display as 255 (white)
        # prob=0.5 means unknown -> display as 128 (gray)
        display = ((1.0 - prob_map) * 255).astype(np.uint8)

        # Convert to color image so we can draw colored markers
        display_color = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)

        # Draw robot position as a green circle
        robot_cx, robot_cy = self.world_to_grid(self.robot_x, self.robot_y)
        if self.is_in_grid(robot_cx, robot_cy):
            cv2.circle(display_color, (robot_cx, robot_cy), 3, (0, 255, 0), -1)

            # Draw a line showing the robot's heading
            head_x = int(robot_cx + 8 * math.cos(self.robot_yaw))
            head_y = int(robot_cy + 8 * math.sin(self.robot_yaw))
            cv2.line(display_color, (robot_cx, robot_cy), (head_x, head_y),
                     (0, 255, 0), 1)

        # Flip vertically so Y-axis points up (matching world frame)
        display_color = cv2.flip(display_color, 0)

        cv2.imshow('Occupancy Grid Map', display_color)
        cv2.waitKey(1)

    # =======================================================================
    # CLEANUP
    # =======================================================================
    def destroy_node(self):
        cv2.destroyAllWindows()
        super().destroy_node()


# ===========================================================================
# MAIN
# ===========================================================================
def main(args=None):
    rclpy.init(args=args)
    mapper = OccupancyGridMapper()

    try:
        rclpy.spin(mapper)
    except KeyboardInterrupt:
        pass

    mapper.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
