# action config

action_config = {
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
    "go_to_coffee_point": {
        'base_prim': '/World/WorkingArea/MainBoard/CoffeePoint',
        'steps':[
            {
                'action_type': 'move',
                'duration': 200,
                'position': [0.2, 0, 0.1],
                'orientation': [0, -0.7071, 0, 0.7071], # wxyz
            }
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
                'position': [-0.2, 0, 0.05],
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