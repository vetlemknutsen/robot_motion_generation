TIAGO = {
    "name": "TIAGo",
    "chains": {
        "right": ["arm_1_joint","arm_2_joint","arm_3_joint","arm_4_joint","arm_5_joint","arm_6_joint","arm_7_joint"],
    },
    "orientation_options": [
        [0.5, -0.5, -0.5, 0.5],   
        [0.0, -0.707, 0.0, 0.707],
        [0.5, -0.5, 0.5, 0.5],   
        [0.5, -0.5, -0.5, -0.5],
    ],
    "default_orientation": [0.5, -0.5, -0.5, 0.5], 
    "limits": {
        "arm_1_joint": (0.0, 2.67),
        "arm_2_joint": (-1.4, 1.01),
        "arm_3_joint": (-3.53, 1.5),
        "arm_4_joint": (-0.32, 2.35),
        "arm_5_joint": (-2.09, 2.09),
        "arm_6_joint": (-1.39, 1.39),
        "arm_7_joint": (-2.07, 2.07),
    },
    "workspace_limits": {
        "x": (0.25, 0.7),
        "y": (-0.5, 0.5),
        "z": (0.4, 1.2),
    },
    "end_effectors": {
        "right": ("torso_lift_link", "gripper_tool_link"),
    },
    "grippers": {
        "right": {
            "joints": ["gripper_left_finger_joint", "gripper_right_finger_joint"],
            "open": 0.044,
            "closed": 0.0,
        },
    },
    "base_frame": "base_footprint",
    "moveit_group": "arm_torso",
}

NAO = {
    "name": "NAO",
    "moveit_group": "right_arm",
    "base_frame": "base_link",
    "chains": {
        "right": [
            "RShoulderPitch",
            "RShoulderRoll",
            "RElbowYaw",
            "RElbowRoll",
            "RWristYaw",
        ],
    },
    "limits": {
        "RShoulderPitch": (-2.0857, 2.0857),
        "RShoulderRoll": (-1.3265, 0.3142),
        "RElbowYaw": (-2.0857, 2.0857),
        "RElbowRoll": (0.0349, 1.5446),
        "RWristYaw": (-1.8238, 1.8238),
    },
    "workspace_limits": {
        "x": (0.0, 0.1),
        "y": (-0.25, 0.0),
        "z": (0.0, 0.17),
    },
    "end_effectors": {
        "right": ("base_link", "r_wrist"),
    },
    "grippers": {},
    "default_orientation": None,
    "orientation_options": None,
}

UR5E = {
    "name": "UR5e",
    "moveit_group": "arm",
    "base_frame": "base_link",
    "chains": {
        "right": [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_1_joint",
            "wrist_2_joint",
            "wrist_3_joint",
        ],
    },
    "limits": {
        "shoulder_pan_joint": (-6.283, 6.283),
        "shoulder_lift_joint": (-6.283, 6.283),
        "elbow_joint": (-3.142, 3.142),
        "wrist_1_joint": (-6.283, 6.283),
        "wrist_2_joint": (-6.283, 6.283),
        "wrist_3_joint": (-6.283, 6.283),
    },
    "workspace_limits": {
        "x": (-0.85, 0.85),
        "y": (-0.85, 0.85),
        "z": (0.0, 0.85),
    },
    "end_effectors": {
        "right": ("base_link", "tool0"),
    },
    "grippers": {
        "right": {
            "joints": ["finger_1_joint_1", "finger_2_joint_1", "finger_middle_joint_1"],
            "open": 0.0495,
            "closed": 1.22,
        },
    },
    "default_orientation": [0.0, 0.707, 0.0, 0.707], 
    "orientation_options": [
        [0.0, 0.707, 0.0, 0.707],   
        [0.0, 0.0, 0.0, 1.0],      
        [0.5, 0.5, -0.5, 0.5],      
    ],
}
