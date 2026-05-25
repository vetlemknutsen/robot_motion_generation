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
from motion_pipeline.pipeline.pipeline import load_robot_config
from motion_pipeline.pipeline.pipeline import run_pipeline
from motion_pipeline.pipeline.pipeline import rml_to_json
from motion_pipeline.storage.sqlite_store import SQLiteMotionStore
from motion_pipeline_msgs.msg import LogMessage
from motion_pipeline_msgs.srv import GenerateRequest, SwitchRobot, GetMotions, SaveMotion, DeleteMotion

class PipelineGeneratorNode(Node):
    """ROS node that exposes the motion pipeline as services and topics.

    Services:
        generate_rml    - run the full pipeline on an input file and return RML.
        switch_robot    - load a different robot config and restart move_group.
        get_motions     - list all saved motions in the database.
        save_motion     - save a motion to the database.
        delete_motion   - delete a motion by id.

    Topics:
        rml_for_execution (sub) - RML text the GUI wants to run.
        motion_commands   (pub) - parsed RML JSON for the executor to consume.
        pipeline_logs     (pub) - human-readable status/error messages for the GUI.
    """
    def __init__(self):
        super().__init__("motion_pipeline_generator")
        # SQLite store for saved motions, kept in the user's home folder
        self.db = SQLiteMotionStore("~/motions.db")

        # one service per pipeline action
        self.generate_srv = self.create_service(GenerateRequest, "generate_rml", self.on_generate_request)
        self.switch_srv = self.create_service(SwitchRobot, "switch_robot", self.on_switch_robot)
        
        # database CRUD services
        self.get_motions_srv = self.create_service(GetMotions, "get_motions", self.on_get_motions)
        self.save_motion_srv = self.create_service(SaveMotion, "save_motion", self.on_save_motion)
        self.delete_motions_srv = self.create_service(DeleteMotion, "delete_motion", self.on_delete_motion)

        # GUI sends RML here when the user hits "send"
        self.send_sub = self.create_subscription(String, "rml_for_execution", self.on_send_request, 10)
        self.send_pub = self.create_publisher(String, "motion_commands", 10)

        # log channel the GUI listens on for status updates
        self.log_pub = self.create_publisher(LogMessage, "pipeline_logs", 10)

        self.current_robot = None
        self.switching = False     # guard so we don't switch twice at once
        self.move_group_process = None # subprocess handle for the running MoveIt

        self.get_logger().info("Generator node started")

        # starts with Tiago by default so the GUI is usable immediately
        self._switch_robot("tiago")
    

    def on_generate_request(self, request, response):
        """Handle a /generate_rml service call.
        Runs the full pipeline (parse → IK → emit → label) and returns the
        resulting RML text. Logs partial failures (some frames unreachable)
        and reports total failure when no frames could be solved.
        Args:
            request: GenerateRequest with input_path, adapter, and robot.
            response: GenerateRequest.Response, filled in and returned.
        Returns:
            The populated response. success=False on any pipeline error.
        """

        self.get_logger().info(f"Generate request: input_path='{request.input_path}")
        # display name is the name from YAML
        display_name = load_robot_config(request.robot).name
        try: 
            rml_text, skipped, total = run_pipeline(Path(request.input_path), request.adapter, request.robot, node=self)
            # all targets unreachable, failure
            if total > 0 and skipped == total:
                self._publish_error(f"Generation failed: no positions reachable for {display_name}")
                response.success = False
                return response
            # some unreachable, still return RML, warn user
            elif skipped > 0:
                self.log_pub.publish(LogMessage(level=LogMessage.ERROR, message=f"{skipped}/{total} position(s) not reachable for {display_name}"))
            response.rml_text = rml_text 
            response.success = True
        except Exception as e: 
            # never let an exception kill the node, tell GUI
            self._publish_error(f"Pipeline failed: {type(e).__name__}: {e}")
            response.success = False
            response.error_message = str(e)
        return response

    def on_send_request(self, msg):
        # GUI sends raw RML, we parse it through Langium and forward the JSON
        rml_plaintext = msg.data
        rml_json = rml_to_json(rml_plaintext)
        out = String()
        out.data = json.dumps(rml_json)
        self.send_pub.publish(out)


    # helper so we don't repeat the LogMessage for errors
    def _publish_error(self, text: str):
        output = LogMessage(level=LogMessage.ERROR, message=text)
        self.log_pub.publish(output)

    def on_switch_robot(self, request, response):
        # ignore if it's the same robot or a switch is in progress
        if request.name != self.current_robot and not self.switching:
            self.switching = True 
            self._switch_robot(request.name)
            self.switching = False 
        response.success = True 
        return response
        

    def _switch_robot(self, robot: str):
        """Stop the current MoveIt and launch the one for the new robot.
        Each robot has its own MoveIt config package, so we kill the running
        move_group subprocess and spawn a fresh one. Blocks until the new
        /compute_ik service is reachable so callers know IK is ready.
        Args:
            robot: Robot key matching a YAML file in configs/robots/.
        """

        display_name = load_robot_config(robot).name
        # kill the old move_group process group
        if self.move_group_process:
            try:
                os.killpg(os.getpgid(self.move_group_process.pid), signal.SIGTERM)
                self.move_group_process.wait(timeout=5)
            except Exception as e:
                self.get_logger().warn("Error killing old move group")


        self.log_pub.publish(LogMessage(level=LogMessage.INFO, message=f"Starting IK solver for {display_name}..."))
        # start_new_session so the child gets its own process group
        self.move_group_process = subprocess.Popen(['ros2', 'launch', f'{robot}_moveit_config', 'move_group.launch.py'], start_new_session=True)

        # block until MoveIt is actually serving /compute_ik
        client = self.create_client(GetPositionIK, '/compute_ik')
        self.get_logger().info("Waiting for /compute_ik service...")
        while not client.wait_for_service(timeout_sec=3.0):
            self.get_logger().info("Still waiting...")

        self.log_pub.publish(LogMessage(level=LogMessage.INFO, message=f"IK solver for robot: {display_name} ready!"))
        # we only used the client to wait, destroy it
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
        # MultiThreadedExecutor so service callbacks can run while other 
        # callbacks are still active
        executor = MultiThreadedExecutor()
        executor.add_node(node)
        executor.spin()
    finally:
        # clean up the MoveIt subprocess and DB connection on shutdown
        if node.move_group_process:
            node.move_group_process.terminate()
        node.db.close()
        node.destroy_node()
        rclpy.shutdown()
