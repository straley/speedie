#!/usr/bin/sudo /usr/bin/python
import time
import yaml
from movement.servos import Servos

servos = Servos(yaml.load(file('servos.yaml', 'r')))
# servos.center()

step = {
    'front-right': {
        'x': 1,
        'y': 1,
        'z': 1,
    },
    'front-left': {
        'x': 0,
        'y': 0,
        'z': 0,
    },
    'rear-right': {
        'x': 0,
        'y': 0,
        'z': 0,
    },
    'rear-left': {
        'x': 1,
        'y': 1,
        'z': 1,
    },
}

servos.display_ik(servos.ik(yaw=-0))

#print servos.body_ik(0, 0, 0, 0, 0, 0);
#print servos.body_ik(0, 0, 0, 0, 0.1, 0);

#servos.move('rear-left', 'hip', 90);
#servos.move('rear-right', 'hip', 90);
