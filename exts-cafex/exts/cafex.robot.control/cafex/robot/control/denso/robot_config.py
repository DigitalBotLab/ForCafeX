# denso robot config

DENSO_ROBOT_CONFIG = {
    "gripper_dof_names": [
        "finger_joint", "right_outer_knuckle_joint",
        "left_inner_knuckle_joint", "right_inner_knuckle_joint",
        #"left_outer_finger_joint", "right_outer_finger_joint", 
        "left_inner_finger_joint", "right_inner_finger_joint",
    ],
    "gripper_open_position": [
        [0.3, -0.3, -0.3, -0.3, 0.3, 0.3]
    ],
    "gripper_closed_position": [
        [0.78, -0.78, -0.78, -0.78, 0.78, 0.78]
    ]
}