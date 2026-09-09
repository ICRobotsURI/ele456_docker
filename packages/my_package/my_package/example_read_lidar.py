import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan

#############################################
# this is a class that is created at the beginning
#############################################
class ReadLaserScan(Node):
	
	# this is executed once when and only once the class is created
	def __init__(self):
		super().__init__('read_laser_scan')
		# create one subscriber
		self.lidar_sub = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
		self.lidar_sub
		
	#############################################
	# this functiion is executed every time that a message is received.
	# all the action in this program happens here
	def scan_callback(self, msg):
		self.get_logger().info('I heard: "%s"' % msg.ranges)

#############################################
# This is the mainn function. It is the first function
# that is called when the program starts		
#############################################
def main(args=None):

	# initialize the node
	rclpy.init(args=args)
	
	# create an innstance of the class
	read_laser_scan = ReadLaserScan()
	
	# 
	rclpy.spin(read_laser_scan)
	
	# if for somme reason the programs exits from the infinte loop
	# cleanup the ROS node 
	read_laser_scan.destroy_node()
	rclpy.shutdown()
	
if __name__ == '__main__':
	main() 



