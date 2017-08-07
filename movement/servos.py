import math
try:
    import Adafruit_PCA9685
except ImportError:
    from utils.mockpwm import MockPWM as Adafruit_PCA9685

class Servos(object):
    def __init__(self, config):
        self.freq = config['controller']['frequency'] if 'controller' in config and 'frequency' in config['controller'] else 120
        self.address = config['controller']['address'] if 'controller' in config and 'address' in config['controller'] else 0x40

        self.pwm = Adafruit_PCA9685.PCA9685(address=self.address)

        self.servos = config['servos']
        self.bones = config['bones']            # length of bones
        self.offsets = config['offsets']        # distance from center of mass
        self.feet = config['feet']              # location of ground contact
        self.axes = {
            'roll': 0,
            'pitch': 0,
            'yaw': 0
        }
        self.position = {
            'x': 0,
            'y': 0,
            'z': 0
        }

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


    #def body_ik(self, x, y, z, delta_x, delta_y, yaw):
    def body_ik(self, step, yaw):

        cos_roll = math.cos(self.axes['roll'])
        sin_roll = math.sin(self.axes['roll'])
        cos_pitch = math.cos(self.axes['pitch'])
        sin_pitch = math.sin(self.axes['pitch'])
        cos_yaw = math.cos(self.axes['yaw'] + yaw)
        sin_yaw = math.sin(self.axes['yaw'] + yaw)


        ik = {}

        for leg in ['front-right', 'front-left', 'rear-right', 'rear-left']:
            x = self.feet[leg]['x'] + step[leg]['x']
            y = self.feet[leg]['y'] + step[leg]['y']
            z = self.feet[leg]['z'] + step[leg]['z']

            target_x = x + self.offsets[leg]['x'] + self.position['x']
            target_y = y + self.offsets[leg]['y'] + self.position['y']
            target_z = z + self.position['z']

            body_x =  self.position['x'] + target_x - \
                     ( target_x * cos_pitch * cos_yaw ) - \
                     ( target_y * sin_roll * sin_pitch * cos_yaw ) - \
                     ( target_z * cos_roll * sin_pitch * cos_yaw ) + \
                     ( target_y * cos_roll * sin_yaw) - \
                     ( target_z * sin_roll * sin_yaw)

            body_y = self.position['y'] + target_y - \
                     ( target_x * cos_pitch * sin_yaw ) - \
                     ( target_y * sin_roll * sin_pitch * sin_yaw) - \
                     ( target_z * cos_roll * sin_pitch * sin_yaw) - \
                     ( target_y * cos_roll * cos_yaw ) + \
                     ( target_z * sin_roll * cos_yaw )

            body_z =  self.position['z'] + target_z + \
                     ( target_x * sin_pitch ) - \
                     ( target_y * sin_roll * cos_pitch) - \
                     ( target_z * cos_roll * cos_pitch)

            len_a = math.sqrt(body_x * body_x + body_y * body_y) - self.bones['coxa']
            len_b = math.sqrt(len_a * len_a + body_z * body_z)
            coxa = math.atan2(body_x, body_y)
            print ( \
                    ( self.bones['femur'] * self.bones['femur'] ) - \
                    ( self.bones['tibia'] * self.bones['tibia'] ) + \
                    ( len_b * len_b )
                ) / ( 2 * self.bones['femur'] * len_b )
            print body_z, len_a
            femur = math.acos( ( \
                ( self.bones['femur'] * self.bones['femur'] ) - \
                ( self.bones['tibia'] * self.bones['tibia'] ) + \
                ( len_b * len_b )
            ) / ( 2 * self.bones['femur'] * len_b ) ) - math.atan2(body_z, len_a)

            ik[leg] = {
                'coxa': coxa,
                'femur': femur,
                'len_a': len_a,
                'len_b': len_b
            }

        return ik
