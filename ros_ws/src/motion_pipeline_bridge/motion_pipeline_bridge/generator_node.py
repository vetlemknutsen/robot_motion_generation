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
from motion_pipeline_msgs.msg import PipelineLog
from motion_pipeline_msgs.srv import GenerateRequest, SwitchRobot

class PipelineGeneratorNode(Node):
    def __init__(self):
        super().__init__("motion_pipeline_generator")

        self.generate_srv = self.create_service(GenerateRequest, "generate_rml", self.on_generate_request)
        self.switch_srv = self.create_service(SwitchRobot, "switch_robot", self.on_switch_robot)
        

        self.send_sub = self.create_subscription(String, "send_webots", self.on_send_request, 10)
        self.send_pub = self.create_publisher(String, "webots_motion", 10)

        self.log_pub = self.create_publisher(PipelineLog, "pipeline_logs", 10)

        self.current_robot = None
        self.switching = False
        self.move_group_process = None

        self.get_logger().info("Generator node started")

        self._switch_robot("nao")

    def on_generate_request(self, request, response):
        self.get_logger().info(f"Generate request: input_path='{request.input_path}")

        try: 
            rml_text = generate_rml(Path(request.input_path), request.adapter, request.robot)
            response.rml_text = rml_text 
            response.success = True
        except Exception as e: 
            self._publish_error(f"Pipeline failed: {type(e).__name__}: {e}")
            response.success = False
            response.error_message = str(e)
        return response

    def on_send_request(self, msg):
        rml_plaintext = msg.data
        rml_json = generate_rml_json_from_plaintext(rml_plaintext)
        out = String()
        out.data = json.dumps(rml_json)
        self.send_pub.publish(out)


    def _publish_error(self, text: str):
        output = PipelineLog(level=PipelineLog.ERROR, message=text)
        self.log_pub.publish(output)

    def on_switch_robot(self, request, response):
        if request.name != self.current_robot and not self.switching:
            self.switching = True 
            self._switch_robot(request.name)
            self.switching = False 
        response.success = True 
        return response
        

    def _switch_robot(self, robot: str):
        if self.move_group_process:
            try:
                os.killpg(os.getpgid(self.move_group_process.pid), signal.SIGTERM)
                self.move_group_process.wait(timeout=5)
            except Exception as e:
                self.get_logger().warn("Error killing old move group")


        self.log_pub.publish(PipelineLog(level=PipelineLog.INFO, message=f"Starting IK solver for {robot}..."))
        self.move_group_process = subprocess.Popen(['ros2', 'launch', f'{robot}_moveit_config', 'move_group.launch.py'], start_new_session=True)

        client = self.create_client(GetPositionIK, '/compute_ik')
        self.get_logger().info("Waiting for /compute_ik service...")
        while not client.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Still waiting...")

        self.log_pub.publish(PipelineLog(level=PipelineLog.INFO, message=f"IK solver for robot: {robot} ready!"))
        self.destroy_client(client)

        self.current_robot = robot
        

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
