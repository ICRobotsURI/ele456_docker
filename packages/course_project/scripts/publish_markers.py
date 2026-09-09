#!/usr/bin/env python3
"""
Publishes cylinder obstacle positions as MarkerArray in rviz.
Reads cylinder positions from a YAML file or from the world SDF directly.
"""

import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker, MarkerArray
from std_msgs.msg import ColorRGBA
from geometry_msgs.msg import Point
import xml.etree.ElementTree as ET
import os
from ament_index_python.packages import get_package_share_directory


class CylinderMarkerPublisher(Node):

    def __init__(self):
        super().__init__('cylinder_marker_publisher')

        self.declare_parameter('world', 'test_world')
        world_name = self.get_parameter('world').get_parameter_value().string_value

        self.publisher = self.create_publisher(MarkerArray, '/cylinder_markers', 10)

        # Parse world file for cylinder positions
        pkg_path = get_package_share_directory('course_project')
        world_file = os.path.join(pkg_path, 'worlds', f'{world_name}.sdf')

        self.cylinders = self._parse_cylinders(world_file)
        self.get_logger().info(f'Found {len(self.cylinders)} cylinders in {world_name}')

        # Publish at 1 Hz (markers are latched-like with repeated publishing)
        self.timer = self.create_timer(1.0, self.publish_markers)

    def _parse_cylinders(self, world_file):
        """Parse SDF world file and extract cylinder model positions."""
        cylinders = []
        try:
            tree = ET.parse(world_file)
            root = tree.getroot()
            for model in root.iter('model'):
                name = model.get('name', '')
                if 'cylinder' in name.lower():
                    pose_elem = model.find('pose')
                    if pose_elem is not None:
                        parts = pose_elem.text.strip().split()
                        x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
                        cylinders.append((name, x, y, z))
        except Exception as e:
            self.get_logger().error(f'Failed to parse world file: {e}')
        return cylinders

    def publish_markers(self):
        marker_array = MarkerArray()

        for i, (name, x, y, z) in enumerate(self.cylinders):
            # Cylinder marker
            marker = Marker()
            marker.header.frame_id = 'odom'
            marker.header.stamp = self.get_clock().now().to_msg()
            marker.ns = 'cylinders'
            marker.id = i
            marker.type = Marker.CYLINDER
            marker.action = Marker.ADD
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = z
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.2  # diameter
            marker.scale.y = 0.2
            marker.scale.z = 0.5  # height
            marker.color = ColorRGBA(r=1.0, g=0.5, b=0.0, a=0.7)
            marker.lifetime.sec = 2  # disappears if node stops

            marker_array.markers.append(marker)

            # Text label above cylinder
            text_marker = Marker()
            text_marker.header.frame_id = 'odom'
            text_marker.header.stamp = self.get_clock().now().to_msg()
            text_marker.ns = 'cylinder_labels'
            text_marker.id = i
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD
            text_marker.pose.position.x = x
            text_marker.pose.position.y = y
            text_marker.pose.position.z = z + 0.4
            text_marker.scale.z = 0.15
            text_marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
            text_marker.text = f'{i+1}'
            text_marker.lifetime.sec = 2

            marker_array.markers.append(text_marker)

        self.publisher.publish(marker_array)


def main(args=None):
    rclpy.init(args=args)
    node = CylinderMarkerPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
