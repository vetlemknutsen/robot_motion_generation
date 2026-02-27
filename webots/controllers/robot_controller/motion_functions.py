'''
MOTION FUNCTIONS

A Motion Function is a python function that makes a robot do an animation.

On Motion Functions:
    * Contains Keyframes in which motors positions are set. 
    * Each Keyframe should use sync=True or motor_set_position_sync() ONCE to avoid async issues. Motions are skipped if not used.
    * The last keyframe resets all motors used in the motion to the default position.
    * You should also be able to adjust motor acceleration and more by using the Webots API.

Future Work: 
    * Motions should be created using a GUI / editor 
    * Motion functions should be generated after creating them in the GUI / editor
'''


'''
This function abstracts the syntax required to create motion functions, allowing more non-experts to create motion functions.

Arguments are represented with strings instead of enums to avoid extra syntax for non-coders.

Arguments "acceleration" and "speed" are not used. You should be able to use the webots API to enable them.
'''
def move(robot, sync, position, joint, rotation='', side='', delay=5000, acceleration=None, speed=None):
    '''
    Moves the specified joint.

    ARGS:
        * robot       (robot):                       The robot to move the joint.
        * sync        (True or False):               Whether this motion is the last motion in the current keyframe.
        * position    (float):                       What position to move the joint to.
        * joint       (string):                      The joint to move ("Shoulder", "Ankle"...)
        * rotation    ("Roll", "Pitch" or "Yaw"):    Which rotation to apply to joint. (Optional)
        * side        ("R" or "L"):                  Which of the left or right joint to move. (Optional)
        * delay       (integer):                     The delay before moving on to next instruction. (Optional)
        * acceleration(float):                       Max acceleration of joint. (Optional) (Not Used)
        * speed       (float):                       Max speed of joint. (Optional) (Not Used)
    '''
    if side in ('R', 'L'):
        motor = side
    elif side != '':
        raise Exception("Argument 'side' should be 'R' or 'L' or not specified...")
    else:
        motor = ''

    motor += joint

    if rotation in ('Roll', 'Pitch', 'Yaw') or rotation.startswith('Finger'):
        motor += rotation
    elif rotation != '':
        raise Exception("Argument 'rotation' should be 'Roll', 'Pitch', 'Yaw', or 'Finger[0-9]+' or not specified...")
    
    try:
        if not sync:
            robot.motors[motor].setPosition(position)
        else:
            robot.motor_set_position_sync(robot.motors[motor], robot.sensors[motor], position, delay)
    except:
        raise Exception(f'Wrong args. Your args resulted in trying to move "{motor}"...')




def adrian(robot):
	# Keyframe
	move(robot, False, 2.4695, 'Shoulder', 'Pitch', 'R')
	move(robot, False, -0.0671, 'Shoulder', 'Roll', 'R')
	move(robot, False, -3.3613, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.5369, 'Elbow', 'Pitch', 'R')
	move(robot, False, 0.6828, 'Elbow', 'Yaw', 'R')
	move(robot, False, 1.3364, 'Wrist', 'Pitch', 'R')
	move(robot, True, -0.0596, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0, 'Gripper', 'Finger2', 'R')
	# Keyframe
	move(robot, False, 2.4702, 'Shoulder', 'Pitch', 'R')
	move(robot, False, -0.0669, 'Shoulder', 'Roll', 'R')
	move(robot, False, -3.3605, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.5343, 'Elbow', 'Pitch', 'R')
	move(robot, False, 0.6814, 'Elbow', 'Yaw', 'R')
	move(robot, False, 1.3354, 'Wrist', 'Pitch', 'R')
	move(robot, True, -0.057, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0.044, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0.044, 'Gripper', 'Finger2', 'R')
	# Keyframe
	move(robot, False, 2.4716, 'Shoulder', 'Pitch', 'R')
	move(robot, False, -0.0665, 'Shoulder', 'Roll', 'R')
	move(robot, False, -3.3589, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.529, 'Elbow', 'Pitch', 'R')
	move(robot, False, 0.6788, 'Elbow', 'Yaw', 'R')
	move(robot, False, 1.3336, 'Wrist', 'Pitch', 'R')
	move(robot, True, -0.0517, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0, 'Gripper', 'Finger2', 'R')
	# Keyframe
	move(robot, False, 0.3904, 'Shoulder', 'Pitch', 'R')
	move(robot, False, 0.0807, 'Shoulder', 'Roll', 'R')
	move(robot, False, -2.6369, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.4569, 'Elbow', 'Pitch', 'R')
	move(robot, False, -0.3799, 'Elbow', 'Yaw', 'R')
	move(robot, False, -1.0921, 'Wrist', 'Pitch', 'R')
	move(robot, True, 1.7326, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0.044, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0.044, 'Gripper', 'Finger2', 'R')
	# Keyframe
	move(robot, False, 0.3693, 'Shoulder', 'Pitch', 'R')
	move(robot, False, 0.0784, 'Shoulder', 'Roll', 'R')
	move(robot, False, -2.6126, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.4458, 'Elbow', 'Pitch', 'R')
	move(robot, False, -0.3525, 'Elbow', 'Yaw', 'R')
	move(robot, False, -1.0614, 'Wrist', 'Pitch', 'R')
	move(robot, True, 1.7173, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0, 'Gripper', 'Finger2', 'R')
	# Keyframe
	move(robot, False, 0.1064, 'Shoulder', 'Pitch', 'R')
	move(robot, False, 0.9419, 'Shoulder', 'Roll', 'R')
	move(robot, False, -1.0628, 'Shoulder', 'Yaw', 'R')
	move(robot, False, 1.26, 'Elbow', 'Pitch', 'R')
	move(robot, False, -0.492, 'Elbow', 'Yaw', 'R')
	move(robot, False, 0.4821, 'Wrist', 'Pitch', 'R')
	move(robot, True, -1.625, 'Wrist', 'Roll', 'R')
	# Keyframe
	move(robot, False, 0.044, 'Gripper', 'Finger1', 'R')
	move(robot, True, 0.044, 'Gripper', 'Finger2', 'R')
