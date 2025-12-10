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
