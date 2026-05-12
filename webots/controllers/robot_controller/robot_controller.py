import threading
import json
import yaml
from controller import Robot
from subscriber import Subscriber
from motion_interpreter import MotionInterpreter
import rclpy


class RobotController(Robot):
    def __init__(self, config):
        self.pending_motion = None
        self.motions = {}

        super().__init__()
        rclpy.init()

        self.subscriber = Subscriber('motion_commands', self.messageCallback)
        self.findAndEnableDevices(config)

        self.interpreter = MotionInterpreter(self.motors, self.sensors, self.motor_set_position_sync, self.motor_set_positions_sync)


    def findAndEnableDevices(self, config):
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

    def messageCallback(self, msg):
        body = json.loads(msg.data)
        if 'def' in body:
            name = body['def']
            self.motions[name] = body 
            self.pending_motion = name


    '''
    Sets motor position and waits for it to reach target position.
    This stops target-positions to be overwritten.

    ARGS:
        tag_motor: (Webots tag) tag of motor to activate
        tag_sensor: (Webots tag) tag of position sensor for motor
        target: (Radians) target position of motor
        delay: (int) optional max wait time in ms (default: no limit)
    '''
    # for Move
    def motor_set_position_sync(self, tag_motor, tag_sensor, target, delay=None):
        self._wait_for_targets([(tag_motor, tag_sensor, target)], delay=delay)

    # for MultiMove
    def motor_set_positions_sync(self, goals, delay=None):
        self._wait_for_targets(goals, delay=delay)

    def _wait_for_targets(self, goals, delay=None, delta=0.001):
        remaining = delay 

        for motor, sensor, target in goals: 
            motor.setPosition(target)
            sensor.enable(self.timeStep)

        while True:
            if self.step(self.timeStep) == -1:
                break 

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

# Create threads
controller_thread = threading.Thread(target=robot_controller.run)
message_listener_thread = threading.Thread(target=robot_controller.subscriber.listener)

# Run threads
controller_thread.start()
message_listener_thread.start()

