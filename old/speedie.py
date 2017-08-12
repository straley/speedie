#!/usr/bin/sudo /usr/bin/python
import time
import yaml
import math
from movement.servos import Servos

servos = Servos(yaml.load(file('servos.yaml', 'r')))

#servos.home()
#time.sleep(1)
#servos.sleep()

for dz in range(10):
    d = servos.ik(dz=dz*1.5, dx=dz*1.5)
    for leg in ['front-right', 'front-left', 'rear-right', 'rear-left']:
        print(d[leg])
        for joint in ['hip', 'knee', 'ankle']:
            rot = math.degrees(d[leg][joint])
            while rot >= 180:
                rot -= 360
            while rot < -180:
                rot += 360

            servos.move(leg, joint, servos.servos[leg][joint]['home'] + rot)

    time.sleep(0.4)

time.sleep(5)
servos.home()
servos.sleep()



#print servos.body_ik(0, 0, 0, 0, 0, 0);
#print servos.body_ik(0, 0, 0, 0, 0.1, 0);

#servos.move('rear-left', 'ankle', 0);
#servos.move('rear-right', 'hip', 90);
