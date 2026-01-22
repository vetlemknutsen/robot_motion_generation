import importlib
import threading
import json
import yaml
import motion_functions
import helpers
from controller import Robot
from subscriber import Subscriber
import rclpy


class RobotController(Robot):
    def __init__(self, config):
        # Instance variable instruction
        self.instruction = ''

        # Instance variable scheduled
        self.scheduled = []

        # Initialize Robot from Webots API
        super().__init__()
        rclpy.init()

        # Initialize subscriber/listener
        self.subscriber = Subscriber('webots_motion', self.messageCallback)

        # Initialize devices (motors, sensors, cameras..)
        self.findAndEnableDevices(config)


    def findAndEnableDevices(self, config):
        # Time step (Webots)
        self.timeStep = int(self.getBasicTimeStep())
        
        # Motors
        self.motors = {}

        # Motor Position Sensors
        self.sensors = {}

        # Populate Motors and motor position sensors from config file (dict of {joint_name : Webots unique_tag})
        for key, val in config['joints'].items():
            if val['motor'] is not None:
                self.motors[key] = self.getDevice(val['motor'])
            if val['sensor'] is not None:
                self.sensors[key] = self.getDevice(val['sensor'])


    # Callback when receiving message through messaging system
    def messageCallback(self, msg):
        body = json.loads(msg)
        if 'instruction' in body:
            self.instruction = body['instruction']
        else:
            helpers.createNewMotion(body)
            importlib.reload(motion_functions)
            if 'def' in body:
                self.instruction = body['def']


    def motor_set_position_sync(self, tag_motor, tag_sensor, target, delay):
        '''
        Sets motor position and waits for it to reach target position.
        This stops target-positions to be overwritten.

        ARGS:
            tag_motor: (Webots tag) tag of motor to activate
            tag_sensor: (Webots tag) tag of position sensor for motor
            target: (Radians) target position of motor
            delay: (int) delay to apply

        USAGE:
            Use for one motion every keyframe (preferably on motor where target position is changed next keyframe). 
        '''
        DELTA = 0.001;  # max tolerated difference
        tag_motor.setPosition(target)
        tag_sensor.enable(self.timeStep)

        condition = True # flag for emulating "do while"

        while condition:
            # Break simulation
            if self.step(self.timeStep) == -1:
                break
            delay -= self.timeStep
            effective = tag_sensor.getValue() # effective position
            condition = (abs(target - effective) > DELTA and delay > 0)
        tag_sensor.disable()


    # Controller loop
    def run(self):
        while True:
            # Schedule instruction
            if len(self.scheduled) > 0:
                if self.instruction == '':
                    self.instruction = self.scheduled.pop(0)
            
            # Perform instruction
            if self.instruction is None:
                print("Could not find matching motion, please check spelling of MoodCard..")
            elif len(self.instruction) > 0:
                print(f'Performing motion "{self.instruction}"')
                eval("motion_functions." + self.instruction + "(self)") # Should be safe as it only invokes non-dunder-functions in ./motion_functions.py
            
            self.instruction = ''

            # Break simulation (https://cyberbotics.com/doc/reference/robot#wb_robot_step)
            if robot_controller.step(self.timeStep) == -1:
                break



######## RUNS ON SIMULATION START ########

# Read main config to get active robot
with open('config.yaml') as f:
  main_config = yaml.safe_load(f)

# Load robot-specific config
robot_name = main_config.get('robot', 'tiago')
with open(f'configs/{robot_name}.yaml') as f:
  config = yaml.safe_load(f)

print(f"Loading robot configuration: {config['name']}")

# Init robot controller
robot_controller = RobotController(config)

# Create threads
controller_thread = threading.Thread(target=robot_controller.run)
message_listener_thread = threading.Thread(target=robot_controller.subscriber.listener)

# Run threads
controller_thread.start()
message_listener_thread.start()

