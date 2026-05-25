import threading
import json
import yaml
from controller import Robot
from subscriber import Subscriber
from motion_interpreter import MotionInterpreter
import rclpy


class RobotController(Robot):
    """Webots controller that runs RML motions received over ROS.
    Subscribes to /motion_commands, stores incoming motions by name,
    and executes them on the simulated robot one at a time. Motor
    keys (e.g. "RShoulderPitch") are looked up in the per-robot YAML
    so the same controller works for every robot.
    """
        
    def __init__(self, config):
        self.pending_motion = None # name of the next motion to run, or None
        self.motions = {}          # name, full RML JSON payload

        super().__init__()
        rclpy.init()

        # Subscriber lives on its own thread
        self.subscriber = Subscriber('motion_commands', self.messageCallback)
        self.findAndEnableDevices(config)

        # Hand the interpreter the motor/sensor dicts and sync helpers
        self.interpreter = MotionInterpreter(self.motors, self.sensors, self.wait_for_targets)


    def findAndEnableDevices(self, config):
        """Look up every joint's motor and sensor device by name.
        Reads the joints section of the robot YAML and grabs the matching
        Webots devices. Motors are capped at 50% of their max velocity so
        the simulation looks smooth instead of snapping to targets.
        Args:
            config: The robot YAML dict.
        """

        self.timeStep = int(self.getBasicTimeStep())
        self.motors = {}
        self.sensors = {}

        for key, val in config['joints'].items():
            if val['motor'] is not None:
                motor = self.getDevice(val['motor'])
                motor.setVelocity(motor.getMaxVelocity() * 0.5)
                self.motors[key] = motor
            if val['sensor'] is not None:
                self.sensors[key] = self.getDevice(val['sensor'])


    # Called from the ROS thread whenever a new motion arrives.
    def messageCallback(self, msg):
        body = json.loads(msg.data)
        if 'def' in body:
            name = body['def']
            self.motions[name] = body 
            self.pending_motion = name

    def wait_for_targets(self, goals, delay=None, delta=0.001):
        """Drive a set of motors to their targets and block until reached.
        Returns when every sensor reads within delta of its
        target, or when delay (ms) runs out, or if Webots is shutting down.
        Args:
            goals: List of (motor, sensor, target_position) tuples.
            delay: Optional timeout in ms. None means wait indefinitely.
            delta: Tolerance in radians for "close enough".
        """
        remaining = delay 

        # send all motors to their targets and turn on the sensors we need to read
        for motor, sensor, target in goals: 
            motor.setPosition(target)
            sensor.enable(self.timeStep)

        while True:
            if self.step(self.timeStep) == -1:
                break 

            # done when every motor is within delta of its target
            all_reached = all(abs(target - sensor.getValue()) <= delta
                                for _, sensor, target in goals) 
            if all_reached:
                break 

            if remaining is not None:
                remaining -= self.timeStep 
                if remaining <= 0:
                    break 

        for _, sensor, _ in goals:
            sensor.disable()
 


    def run(self):
        while True:
            if self.pending_motion:
                name = self.pending_motion 
                self.pending_motion = None
            
                if name in self.motions:
                    print(f'Performing motion "{name}"')
                    self.interpreter.execute(self.motions[name])
                else: 
                    print(f'Unknown motion: "{name}"')

            # Break simulation (https://cyberbotics.com/doc/reference/robot#wb_robot_step)
            if self.step(self.timeStep) == -1:
                break



######## RUNS ON SIMULATION START ########
with open('config.yaml') as f:
  main_config = yaml.safe_load(f)

# Load robot-specific config
robot_name = main_config.get('robot', 'tiago')
with open(f'configs/{robot_name}.yaml') as f:
  config = yaml.safe_load(f)

print(f"Loading robot configuration: {config['name']}")

# Init robot controller
robot_controller = RobotController(config)

# Two threads: one drives the simulation, the other spins ROS.
# Webots's step() must run on whichever thread owns the Robot object,
# so we keep that on controller_thread and let ROS spin separately
controller_thread = threading.Thread(target=robot_controller.run)
message_listener_thread = threading.Thread(target=robot_controller.subscriber.listener)

# Run threads
controller_thread.start()
message_listener_thread.start()

