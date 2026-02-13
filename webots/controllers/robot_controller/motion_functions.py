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





