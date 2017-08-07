#!/usr/bin/sudo /usr/bin/python
import time
import yaml
from movement.servos import Servos

servos = Servos(yaml.load(file('servos.yaml', 'r')))

print "test"
servos.move('rear-left', 'hip', 90);
servos.move('rear-right', 'hip', 90);

time.sleep( 1.5 )
print "center"
servos.center()
