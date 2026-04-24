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
from rclpy.executors import MultiThreadedExecutor
from motion_pipeline.runtime.generate import build_robot_config
from motion_pipeline.runtime.generate import generate_output
from motion_pipeline.runtime.generate import generate_rml_json_from_plaintext
from motion_pipeline_bridge.database_logic import SQLiteMotionStore
from motion_pipeline_msgs.msg import LogMessage
from motion_pipeline_msgs.srv import GenerateRequest, SwitchRobot, GetMotions, SaveMotion, DeleteMotion

class PipelineGeneratorNode(Node):
    def __init__(self):
        super().__init__("motion_pipeline_generator")
        self.db = SQLiteMotionStore("~/motions.db")

        self.generate_srv = self.create_service(GenerateRequest, "generate_rml", self.on_generate_request)
        self.switch_srv = self.create_service(SwitchRobot, "switch_robot", self.on_switch_robot)
        
        self.get_motions_srv = self.create_service(GetMotions, "get_motions", self.on_get_motions)
        self.save_motion_srv = self.create_service(SaveMotion, "save_motion", self.on_save_motion)
        self.delete_motions_srv = self.create_service(DeleteMotion, "delete_motion", self.on_delete_motion)


        self.send_sub = self.create_subscription(String, "rml_for_execution", self.on_send_request, 10)
        self.send_pub = self.create_publisher(String, "motion_commands", 10)

        self.log_pub = self.create_publisher(LogMessage, "pipeline_logs", 10)

        self.current_robot = None
        self.switching = False
        self.move_group_process = None

        self.get_logger().info("Generator node started")

        self._switch_robot("tiago")
    

    def on_generate_request(self, request, response):
        self.get_logger().info(f"Generate request: input_path='{request.input_path}")
        display_name = build_robot_config(request.robot).name
        try: 
            rml_text, skipped, total = generate_output(Path(request.input_path), request.adapter, request.robot, node=self)
            if total > 0 and skipped == total:
                self._publish_error(f"Generation failed: no positions reachable for {display_name}")
                response.success = False
                return response
            elif skipped > 0:
                self.log_pub.publish(LogMessage(level=LogMessage.ERROR, message=f"{skipped}/{total} position(s) not reachable for {display_name}"))
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
        output = LogMessage(level=LogMessage.ERROR, message=text)
        self.log_pub.publish(output)

    def on_switch_robot(self, request, response):
        if request.name != self.current_robot and not self.switching:
            self.switching = True 
            self._switch_robot(request.name)
            self.switching = False 
        response.success = True 
        return response
        

    def _switch_robot(self, robot: str):
        display_name = build_robot_config(robot).name
        if self.move_group_process:
            try:
                os.killpg(os.getpgid(self.move_group_process.pid), signal.SIGTERM)
                self.move_group_process.wait(timeout=5)
            except Exception as e:
                self.get_logger().warn("Error killing old move group")


        self.log_pub.publish(LogMessage(level=LogMessage.INFO, message=f"Starting IK solver for {display_name}..."))
        self.move_group_process = subprocess.Popen(['ros2', 'launch', f'{robot}_moveit_config', 'move_group.launch.py'], start_new_session=True)

        client = self.create_client(GetPositionIK, '/compute_ik')
        self.get_logger().info("Waiting for /compute_ik service...")
        while not client.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Still waiting...")

        self.log_pub.publish(LogMessage(level=LogMessage.INFO, message=f"IK solver for robot: {display_name} ready!"))
        self.destroy_client(client)

        self.current_robot = robot


    # Database handlers 
    def on_get_motions(self, request, response):
        rows = self.db.get_all()
        for row in rows: 
            response.ids.append(row[0])
            response.names.append(row[1])
            response.robots.append(row[2])
            response.rmls.append(row[3])
        return response 
    
    def on_save_motion(self, request, response):
        self.db.insert(request.name, request.robot, request.rml)
        response.success = True
        return response 
    
    def on_delete_motion(self,request, response):
        self.db.delete(request.id)
        response.success = True 
        return response

        

def main():
    rclpy.init()
    node = PipelineGeneratorNode()
    try: 
        executor = MultiThreadedExecutor()
        executor.add_node(node)
        executor.spin()
    finally:
        if node.move_group_process:
            node.move_group_process.terminate()
        node.db.close()
        node.destroy_node()
        rclpy.shutdown()
