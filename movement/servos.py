import math
import Adafruit_PCA9685

class Servos(object):

    def __init__(self, config):
        self.freq = config['controller']['frequency'] if 'controller' in config and 'frequency' in config['controller'] else 120
        self.address = config['controller']['address'] if 'controller' in config and 'address' in config['controller'] else 0x40
        self.pwm = Adafruit_PCA9685.PCA9685(address=self.address)
        self.servos = config['servos']
        self.bones = config['bones']

    def move(self, leg, joint, degrees):
        if not self.servos[leg] or not self.servos[leg][joint]:
            return false

        freqratio = self.freq / 60

        servo = self.servos[leg][joint]
        min = servo['min']
        max = servo['max']
        range = math.radians(servo['range'])
        channel = servo['channel']
        position = math.radians(degrees)

        if position < 0:
            position = 0
        elif position > range:
            position = range

        if max < min:
            temp = max
            max = min
            min = temp
            position = range - position

        percent_of_range = position / range
        target = int ( ( ( ( max - min ) * percent_of_range ) + min ) * freqratio )
        self.pwm.set_pwm(channel, 0, target)


    def center(self, leg=False, joint=False):
        if not leg:
            legs = ['front-right', 'front-left', 'rear-right', 'rear-left']
        else:
            legs = [leg]

        if not joint:
            joints = ['hip', 'ankle', 'knee']
        else:
            joints = [joint]


        for leg in legs:
            for joint in joints:
                self.move(leg, joint, self.servos[leg][joint]['center']);
