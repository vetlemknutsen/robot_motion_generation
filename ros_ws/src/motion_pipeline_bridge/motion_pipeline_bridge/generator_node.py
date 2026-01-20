import json
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from motion_pipeline.runtime.generate import generate_rml


class PipelineGeneratorNode(Node):
    def __init__(self):
        super().__init__("motion_pipeline_generator")
        self.sub = self.create_subscription(String, "generate_request", self.on_request, 10)
        self.pub = self.create_publisher(String, "rml_output", 10)
        self.get_logger().info("Generator node started")

    def on_request(self, msg: String):
        try: 
            req = json.loads(msg.data)
            input_path = Path(req["input_path"])
            adapter = req["adapter"]
            robot = req["robot"]
        except Exception as e: 
            self._publish_error("Bad JSON request")
            return
        
        try: 
            rml_text = generate_rml(input_path, adapter, robot)
        except Exception as e:
            self._publish_error("Pipeline failed")

        try:
            out = String()
            out.data = rml_text 
            self.pub.publish(out)
        except Exception as e: 
            self.__publish_error("No rml text")

    def _publish_error(self, text: str):
        self.get_logger().error(text)
        out = String()
        out.data = "ERROR: " + text 
        self.pub.publish(out)

def main():
    rclpy.init()
    node = PipelineGeneratorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
