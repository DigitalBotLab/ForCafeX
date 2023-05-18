# action config

action_config = {
    "low_level_test":{
        'base_prim': None,
        'steps':[
            {
                'action_type': 'low_level',
                'duration': 200,
                'joint_positions': [0, 0, 0, 0, 0, 0],
            }
        ]
    },
    "go_home": {
        'base_prim': None,
        'steps':[
            {
                'action_type': 'move',
                'duration': 200,
                'position': [0.3, 0, 0.3],
                'orientation': [0.7071, 0.0, 0.7071, 0], # wxyz
            },

        ]
    },
    "go_home_reverse": {
        'base_prim': None,
        'steps':[
            {
                'action_type': 'move',
                'duration': 100,
                'position': [0.3, 0, 0.3],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },

        ]
    },
    "place_cup_to_coffee_point": {
        'base_prim': '/World/WorkingArea/MainBoard/CoffeePoint',
        'steps':[
            {
                'action_type': 'move',
                'duration': 100,
                'position': [-0.4, 0, 0.2],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            {
                'action_type': 'move',
                'duration': 50,
                'position': [-0.2, 0, 0.08],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.2, 0, 0.05],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
            # {
            #     'action_type': 'open',
            #     'duration': 60,
            #     'ratio': None,
            # },
            ## no need to move back
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.4, 0, 0.05],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.4, 0, 0.2],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
        ]
    },
    "move_cup_out_coffee_point": {
        'base_prim': '/World/WorkingArea/MainBoard/CoffeePoint',
        'steps':[
            ## no need to move back
            {
                'action_type': 'move',
                'duration': 50,
                'position': [-0.2, 0, 0.12],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            {
                'action_type': 'move',
                'duration': 50,
                'position': [-0.4, 0, 0.2],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
        ]
    },
    "place_cup_to_milk_point": {
        'base_prim': '/World/WorkingArea/MainBoard/MilkPoint',
        'steps':[
            # {
            #     'action_type': 'move',
            #     'duration': 100,
            #     'position': [-0.4, 0, 0.2],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
            {
                'action_type': 'move',
                'duration': 150,
                'position': [-0.2, 0, 0.06],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.2, 0, 0.06],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
            # {
            #     'action_type': 'open',
            #     'duration': 60,
            #     'ratio': None,
            # },
            ## no need to move back
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.4, 0, 0.05],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
            # {
            #     'action_type': 'move',
            #     'duration': 50,
            #     'position': [-0.4, 0, 0.2],
            #     'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            # },
        ]
    },
    "pick_up_cup": {
        'base_prim': '/World/CupCollection/coffee_cup',
        'steps':[
            {
                'action_type': 'move',
                'duration': 100,
                'position': [-0.2, 0, -0.1],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            {
                'action_type': 'open',
                'duration': 60,
                'ratio': None,
            },
            {
                'action_type': 'move',
                'duration': 50,
                'position': [-0.2, 0, 0.07],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            {
                'action_type': 'close',
                'duration': 100,
                'ratio': 0.2,
            },
            {
                'action_type': 'move',
                'duration': 50,
                'position': [-0.2, 0, -0.2],
                'orientation': [0, 0.7071, 0.0, 0.7071], # wxyz
            },
            {
                'action_type': 'move',
                'duration': 200,
                'position': [-0.2, 0, -0.2],
                'orientation': [-0.7071, 0.0, -0.7071, 0.0], # wxyz
            },
        ]
    },
}