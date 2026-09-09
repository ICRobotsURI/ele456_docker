import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class RobotController(Node):
	def __init__(self):
		super().__init__('robot_controller')
		self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)
		self.subscriber = self.create_subscription(LaserScan, 'scan', self.scan_callback, 1)
		timer_period = 0.2
		self.timer = self.create_timer(timer_period, self.control_callback)
		self.i = 0
		
	def scan_callback(self, msg):
		self.get_logger().info('I heard: "%s"' % msg.ranges)
		
	def control_callback(self):
		msg = Twist()
		msg.linear.x = 0.1
		msg.angular.z = 0.2
		self.cmd_vel_pub.publish(msg)
		self.i += 1
		
def main(args=None):
	rclpy.init(args=args)
	robot_controller = RobotController()
	
	rclpy.spin(robot_controller)
	
	robot_controller.destroy_node()
	rclpy.shutdown()
	
if __name__ == '__main__':
	main() 



