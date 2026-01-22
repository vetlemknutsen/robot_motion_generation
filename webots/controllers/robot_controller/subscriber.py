import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class Subscriber(Node):
    def __init__(self, topic, callback):
        super().__init__('webots_motion_sub')
        self._sub = self.create_subscription(String, topic, callback, 10)

    def listener(self):
        rclpy.spin(self)
