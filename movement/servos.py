from __future__ import print_function
import math
import string

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

    def sleep(self):
        try:
            import Adafruit_GPIO.I2C as I2C
            I2C.get_i2c_device(0x00).writeRaw8(0x06)
        except:
            print("[i2c] not available")

    def move(self, leg, joint, degrees):
        if not self.servos[leg] or not self.servos[leg][joint]:
            return false

        freqratio = self.freq / 60

        servo = self.servos[leg][joint]
        min = servo['min'] * freqratio
        max = servo['max'] * freqratio
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

        print ("max, min", max, min)
        target = int ( ( ( ( max - min ) * percent_of_range ) + min ) )
        print ("target", target)
        self.pwm.set_pwm(channel, 0, target)


    # if setting_or_value is a string, it uses that setting
    # if it is an int, it uses that as it's degrees
    # if it is a float, it uses that a a percentage of range

    def use(self, setting_or_value, leg=False, joint=False):
        if not leg:
            legs = ['front-right', 'front-left', 'rear-right', 'rear-left']
        else:
            legs = [leg]

        if not joint:
            joints = ['hip', 'ankle', 'knee']
        else:
            joints = [joint]

        if isinstance(setting_or_value, basestring):
            for leg in legs:
                for joint in joints:
                    self.move(leg, joint, self.servos[leg][joint][setting_or_value])
        elif isinstance(setting_or_value, int):
            for leg in legs:
                for joint in joints:
                    self.move(leg, joint, setting_or_value)
        elif isinstance(setting_or_value, float):
            for leg in legs:
                for joint in joints:
                    self.move(leg, joint, int(setting_or_value * self.servos[leg][joint]['range']))


    def home(self, leg=False, joint=False):
        self.use('home', leg, joint)

    def stand(self, leg=False, joint=False):
        self.use('stand', leg, joint)

    def min(self, leg=False, joint=False):
        self.use(0, leg, joint)

    def max(self, leg=False, joint=False):
        self.use('range', leg, joint)

    def mid(self, leg=False, joint=False):
        self.use(0.5, leg, joint)


    def ik(self, dx=0, dy=0, dz=0, yaw=0, pitch=0, roll=0):
        _tibia_length = self.bones['tibia']
        _femur_length = self.bones['femur']
        _coxa_length = self.bones['coxa']

        ik = {}
        error = False

        for leg in ['front-right', 'front-left', 'rear-right', 'rear-left']:
            x = self.feet[leg]['x'] + dx
            y = self.feet[leg]['y'] + dy
            distality = math.sqrt(x*x + y*y)
            angle_x = (math.pi / 2) - math.atan2(y, x)

            ik_x = self.feet[leg]['x'] - self.offsets[leg]['x'] + dx + (math.sin(angle_x + yaw) * distality) - x
            ik_y = self.feet[leg]['y'] - self.offsets[leg]['y']  + dy + (math.cos(angle_x + yaw) * distality) - y
            ik_z = self.feet[leg]['z'] + dz + (math.tan(pitch) * x)  + (math.tan(roll) * y)

            # will this ever change?  ==sqrt(feetx2 + feety2)
            coxa_foot_dist = math.sqrt( ik_x * ik_x + ik_y * ik_y )
            femur_foot_distance = coxa_foot_dist - _coxa_length

            iksw = math.sqrt( femur_foot_distance * femur_foot_distance + ik_z * ik_z )

            _ankle_n = iksw * iksw - _tibia_length * _tibia_length - _femur_length * _femur_length
            _ankle_d = 2 * _femur_length * _tibia_length
            _ankle_f = _ankle_n / _ankle_d

            if abs(_ankle_f) > 1:
                error = True
                break

            ankle = math.acos( _ankle_f ) + math.radians(self.servos[leg]['ankle']['default'])

            _knee_n = _tibia_length * _tibia_length - _femur_length * _femur_length - iksw * iksw
            _knee_d = 2 * _femur_length * iksw
            _knee_f = _knee_n / _knee_d

            if abs(_knee_f) > 1:
                error = True
                break

            knee =  math.atan(femur_foot_distance / ik_z) + math.acos(_knee_f) + math.radians(self.servos[leg]['knee']['default'])
            hip = math.atan2(ik_y, ik_x) + math.radians(self.servos[leg]['hip']['default'])



            ik[leg] = {
                'x': ik_x + self.offsets[leg]['x'],
                'y': ik_y + self.offsets[leg]['y'],
                'z': ik_z,
                'knee': ankle,
                'ankle': - (math.radians(12) - knee),
                'hip': hip
            }

        if error:
            return False
        else:
            return ik


    def display_ik(self, ik):
        if ik:
            info = {
                8: 'REAR LEFT                                         FRONT LEFT',
                9: ('HIP  : ' + repr(round(math.degrees(ik['rear-left']['hip']),0))).ljust(50) + \
                    'HIP  : ' + repr(round(math.degrees(ik['front-left']['hip']),0)),
                10: ('KNEE : ' + repr(round(math.degrees(ik['rear-left']['knee']),0))).ljust(50) + \
                    'KNEE : ' + repr(round(math.degrees(ik['front-left']['knee']),0)),
                11: ('ANKLE: ' + repr(round(math.degrees(ik['rear-left']['ankle']),0))).ljust(50) + \
                    'ANKLE: ' + repr(round(math.degrees(ik['front-left']['ankle']),0)),
                28: 'REAR RIGHT                                        FRONT RIGHT',
                29: ('HIP  : ' + repr(round(math.degrees(ik['rear-right']['hip']),0))).ljust(50) + \
                    'HIP  : ' + repr(round(math.degrees(ik['front-right']['hip']),0)),
                30: ('KNEE : ' + repr(round(math.degrees(ik['rear-right']['knee']),0))).ljust(50) + \
                    'KNEE : ' + repr(round(math.degrees(ik['front-right']['knee']),0)),
                31: ('ANKLE: ' + repr(round(math.degrees(ik['rear-right']['ankle']),0))).ljust(50) + \
                    'ANKLE: ' + repr(round(math.degrees(ik['front-right']['ankle']),0)),
            }

            grid = [['.']*100 for _ in range(40)]

            for leg in ['front-right', 'front-left', 'rear-right', 'rear-left']:
                x = int(round((self.feet[leg]['x']),0) / 10) + 50
                y = int(round((self.feet[leg]['y']),0) / 10) + 20
                grid[y][x] = "*"

                x = int(round((ik[leg]['x']),0) / 10) + 50
                y = int(round((ik[leg]['y']),0) / 10) + 20
                z = int(round((ik[leg]['z']),0) / 10) + 20
                if z<24:
                    grid[y][x] = string.lowercase[:26][int((z - 24)/10)]
                else:
                    grid[y][x] = string.uppercase[:26][int((z - 24)/10)]


            n = 0
            for r in grid:
                for c in r:
                    print(c, end='')

                if n in info:
                    print('          ' + info[n])
                else:
                    print('')

                n = n + 1
        else:
            print("OUT OF BOUNDS")
