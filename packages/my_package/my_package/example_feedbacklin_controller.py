import rclpy
import math 

from rclpy.node import Node

from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry


class RobotController(Node):
	
	##########################################
	### here define the variable of the robot
	##########################################
	x = 0.0
	y = 0.0
	z = 0.0

	yaw = 0.0
	
	gx = 1.0
	gy = 1.0
	
	k = 0.2
	b = 0.05

	sc = LaserScan()

	##########################################
	### this function intializes the class
	##########################################
	def __init__(self):
		super().__init__('robot_controller')
		self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 1)
		self.subscriber = self.create_subscription(LaserScan, 'scan', self.scan_callback, 1)
		self.subscriber = self.create_subscription(Odometry, 'odom', self.odom_callback, 1)
		timer_period = 0.2
		self.timer = self.create_timer(timer_period, self.control_callback)
		self.i = 0
	
	##########################################
	### this function save the scan any every it is received
	##########################################
	def scan_callback(self, msg):
		sc = msg
		
	##########################################
	### this function save the odometry every time it is received
	##########################################
	def odom_callback(self, msg):
		global x, y, z, yaw
		x = msg.pose.pose.position.x
		y = msg.pose.pose.position.y
		z = msg.pose.pose.position.z
		
		yaw = math.atan2(2.0*(msg.pose.pose.orientation.y*msg.pose.pose.orientation.z + msg.pose.pose.orientation.w*msg.pose.pose.orientation.x), msg.pose.pose.orientation.w*msg.pose.pose.orientation.w - msg.pose.pose.orientation.x*msg.pose.pose.orientation.x - msg.pose.pose.orientation.y*msg.pose.pose.orientation.y + msg.pose.pose.orientation.z*msg.pose.pose.orientation.z);
		
		
	##########################################
	### this function is executed 5 times/second, no matter what
	##########################################
	### NOTE FOR STUDENTS: I have not finished implementing this.
	### It will be given as homework and part of the project
	def control_callback(self):
		print(self.x, self.y, self.z, self.yaw)
		msg = Twist()
		msg.linear.x = 0.1
		msg.angular.z = 0.2
		self.cmd_vel_pub.publish(msg)
		self.i += 1
		
		self.ex = self.gx - self.x
		self.ey = self.gy - self.y
		
		#u = np.array([self.k*self.ex],[self.k*self.ey])
		
		#inp = 



##########################################
### this is the main function and is the entry point in this file
##########################################
def main(args=None):
	rclpy.init(args=args)
	robot_controller = RobotController()
	
	rclpy.spin(robot_controller)
	
	robot_controller.destroy_node()
	rclpy.shutdown()
	
if __name__ == '__main__':
	main() 



