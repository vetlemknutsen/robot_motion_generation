import json
from pathlib import Path
import traceback

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
import time
from moveit_msgs.srv import GetPositionIK
import os 
import signal

from motion_pipeline.runtime.generate import generate_rml
from motion_pipeline.runtime.generate import generate_rml_json_from_plaintext

class PipelineGeneratorNode(Node):
    def __init__(self):
        super().__init__("motion_pipeline_generator")
        self.sub = self.create_subscription(String, "generate_request", self.on_request, 10)
        self.pub = self.create_publisher(String, "rml_output", 10)

        self.send_sub = self.create_subscription(String, "send_webots", self.on_send_request, 10)
        self.send_pub = self.create_publisher(String, "webots_motion", 10)

        self.switch_sub = self.create_subscription(String, "switch_robot", self.on_switch_robot,10)
        self.ready_pub = self.create_publisher(String, "robot_ready", 10)

        self.current_robot = None
        self.switching = False
        self.move_group_process = None

        self.get_logger().info("Generator node started")

        self._switch_robot("nao")

    def on_request(self, msg: String):
        try: 
            req = json.loads(msg.data)
            input_path = Path(req["input_path"])
            adapter = req["adapter"]
            robot = req["robot"]

        except Exception as e: 
            self._publish_error(f"Bad JSON request: {e}")
            return

        self.get_logger().info(
            f"Generate request: input_path='{input_path}', adapter='{adapter}', robot='{robot}'"
        )

        try: 
            rml_text = generate_rml(input_path, adapter, robot)
        except Exception as e:
            self.get_logger().error(
                f"Pipeline failed for input_path='{input_path}', adapter='{adapter}', robot='{robot}': "
                f"{type(e).__name__}: {e}"
            )
            self.get_logger().error(traceback.format_exc())
            self._publish_error(f"Pipeline failed: {type(e).__name__}: {e}")
            return

        try:
            out = String()
            out.data = rml_text 
            self.pub.publish(out)
            self.get_logger().info("RML generation succeeded and published")
        except Exception as e: 
            self._publish_error(f"No rml text: {type(e).__name__}: {e}")

    def on_send_request(self, msg):
        rml_plaintext = msg.data
        rml_json = generate_rml_json_from_plaintext(rml_plaintext)
        out = String()
        out.data = json.dumps(rml_json)
        self.send_pub.publish(out)


    def _publish_error(self, text: str):
        self.get_logger().error(text)
        out = String()
        out.data = "ERROR: " + text 
        self.pub.publish(out)

    def on_switch_robot(self, msg: String):
        robot = msg.data

        if robot == self.current_robot or self.switching:
            return

        self.switching = True
        self._switch_robot(robot)
        self.switching = False

    def _switch_robot(self, robot: str):
        if self.move_group_process:
            try:
                os.killpg(os.getpgid(self.move_group_process.pid), signal.SIGTERM)
                self.move_group_process.wait(timeout=5)
            except Exception as e:
                self.get_logger().warn("Error killing old move group")


        self.get_logger().info(f"Starting new move_group for {robot}...")
        self.move_group_process = subprocess.Popen(['ros2', 'launch', f'{robot}_moveit_config', 'move_group.launch.py'], start_new_session=True)

        client = self.create_client(GetPositionIK, '/compute_ik')
        self.get_logger().info("Waiting for /compute_ik service...")
        while not client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Still waiting...")

        self.get_logger().info("Service ready!")
        self.destroy_client(client)

        self.current_robot = robot
        self.ready_pub.publish(String(data=robot))
        

def main():
    rclpy.init()
    node = PipelineGeneratorNode()
    try: 
        rclpy.spin(node)
    finally:
        if node.move_group_process:
            node.move_group_process.terminate()
        node.destroy_node()
        rclpy.shutdown()
