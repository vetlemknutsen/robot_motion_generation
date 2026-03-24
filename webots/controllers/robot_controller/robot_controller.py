import threading
import json
import yaml
from controller import Robot, Supervisor
from subscriber import Subscriber
from motion_interpreter import MotionInterpreter
import rclpy


class RobotController(Supervisor):
    def __init__(self, config):
        self.pending_motion = None
        self.motions = {}

        super().__init__()
        rclpy.init()

        # Supervisor fields for pinning the robot base
        self.root_node = self.getSelf()
        self.translation_field = self.root_node.getField('translation')
        self.rotation_field = self.root_node.getField('rotation')
        self.pinned = False

        self.subscriber = Subscriber('webots_motion', self.messageCallback)
        self.findAndEnableDevices(config)

        self.interpreter = MotionInterpreter(self.motors, self.sensors, self.motor_set_position_sync)


    def findAndEnableDevices(self, config):
        self.timeStep = int(self.getBasicTimeStep())
        self.motors = {}
        self.sensors = {}

        for key, val in config['joints'].items():
            if val['motor'] is not None:
                motor = self.getDevice(val['motor'])
                motor.setVelocity(motor.getMaxVelocity() * 0.1)
                self.motors[key] = motor
            if val['sensor'] is not None:
                self.sensors[key] = self.getDevice(val['sensor'])

        for motor_name in config.get('locked_joints', []):
            motor = self.getDevice(motor_name)
            if motor is None:
                print(f'WARNING: locked joint motor "{motor_name}" not found')
                continue
            motor.setPosition(0.0)
            print(f'Locked joint: {motor_name}')

    def messageCallback(self, msg):
        body = json.loads(msg.data)
        if 'def' in body:
            name = body['def']
            self.motions[name] = body 
            self.pending_motion = name


    def motor_set_position_sync(self, tag_motor, tag_sensor, target, delay=None):
        '''
        Sets motor position and waits for it to reach target position.
        This stops target-positions to be overwritten.

        ARGS:
            tag_motor: (Webots tag) tag of motor to activate
            tag_sensor: (Webots tag) tag of position sensor for motor
            target: (Radians) target position of motor
            delay: (int) optional max wait time in ms (default: no limit)

        USAGE:
            Use for one motion every keyframe (preferably on motor where target position is changed next keyframe).
        '''
        DELTA = 0.001;  # max tolerated difference
        tag_motor.setPosition(target)
        tag_sensor.enable(self.timeStep)

        while True:
            if self.step(self.timeStep) == -1:
                break
            effective = tag_sensor.getValue()
            if abs(target - effective) <= DELTA:
                break
            if delay is not None:
                delay -= self.timeStep
                if delay <= 0:
                    break
        tag_sensor.disable()


    def run(self):
        # Let the robot settle onto the ground for 1 second
        settle_steps = int(1000 / self.timeStep)
        for _ in range(settle_steps):
            if self.step(self.timeStep) == -1:
                return
        # Capture settled position
        self.pinned_translation = self.translation_field.getSFVec3f()
        self.pinned_rotation = self.rotation_field.getSFRotation()
        print(f'Robot pinned at {self.pinned_translation}')

        while True:
            if self.pending_motion:
                name = self.pending_motion
                self.pending_motion = None

                if name in self.motions:
                    print(f'Performing motion "{name}"')
                    self.interpreter.execute(self.motions[name])
                else:
                    print(f'Unknown motion: "{name}"')

            # Pin the robot base to prevent tipping from arm movement
            self.translation_field.setSFVec3f(self.pinned_translation)
            self.rotation_field.setSFRotation(self.pinned_rotation)

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

# Create threads
controller_thread = threading.Thread(target=robot_controller.run)
message_listener_thread = threading.Thread(target=robot_controller.subscriber.listener)

# Run threads
controller_thread.start()
message_listener_thread.start()

