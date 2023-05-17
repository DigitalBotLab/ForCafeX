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
            {
                'action_type': 'open',
                'duration': 60,
                'ratio': None,
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
}