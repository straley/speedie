from pyax12.connection import Connection
import time

connection = Connection(port='/dev/ttyACM0', baudrate=1000000)

class Joint(object):
    def __init__(self, id, inverted=False, min=-150, max=150, speed=False, connection=False):
        self.id = id
        self.inverted = inverted
        self.min = min
        self.max = max
        self._speed = speed
        self.connection = connection

    def speed(self, value=False):
        self._speed = value

    def goto(self, position, speed=False):
        if self.inverted:
            position = -position
        if position < self.min:
            position = self.min
        elif position > self.max:
            position = self.max

        if speed == False and self._speed != False:
            speed = self._speed

        if self.connection:
            self.connection.goto(self.id, position, speed, True)
        else:
            print("[simulation]", self.id, ", position:", position, ", speed:", speed)

class Joints(object):
    def __init__(self, joints):
        self.joints = joints

    def speed(self, value=False):
        for joint in self.joints:
            joint.speed(value)

    def goto(self, position, speed=False):
        for joint in self.joints:
            joint.goto(position, speed)

class Ankle(Joint):
    def __init__(self, id, inverted=False, speed=False, connection=False):
        super(Ankle, self).__init__(id=id, inverted=inverted, min=-95, max=95, speed=speed, connection=connection)

class Knee(Joint):
    def __init__(self, id, inverted=False, speed=False, connection=False):
        super(Knee, self).__init__(id=id, inverted=inverted, min=-95, max=95, speed=speed, connection=connection)

class Hip(Joint):
    def __init__(self, id, inverted=False, speed=False, connection=False):
        super(Hip, self).__init__(id=id, inverted=inverted, min=-95, max=60, speed=speed, connection=connection)

class Leg(object):
    def __init__(self, start_id, inverted=False, speed=False, connection=False):
        self.start_id = start_id
        self.inverted = inverted
        self._speed = speed
        self.hip = Hip(id=start_id, inverted=inverted, speed=speed, connection=connection)
        self.knee = Knee(id=start_id+1, inverted=inverted, speed=speed, connection=connection)
        self.ankle = Ankle(id=start_id+2, inverted=inverted, speed=speed, connection=connection)

    def speed(self, value=False):
        self.hip.speed(value=value)
        self.knee.speed(value=value)
        self.ankle.speed(value=value)

class Group(object):
    def __init__(self, legs):
        self.legs = legs
        _hips = []
        _knees = []
        _ankles = []
        for leg in legs:
            _hips.append(leg.hip)
            _knees.append(leg.knee)
            _ankles.append(leg.ankle)

        self.hip = Joints(_hips)
        self.knee = Joints(_knees)
        self.ankle = Joints(_ankles)

    def speed(self, value=False):
        for leg in self.legs:
            leg.speed(value)


class Legs(object):
    def __init__(self, start_id, connection=False, speed=False, clockwise=True):
        if clockwise:
            self.fl = Leg(start_id=start_id, speed=speed, connection=connection)
            self.fr = Leg(start_id=start_id+3, speed=speed, inverted=True, connection=connection)
            self.rl = Leg(start_id=start_id+(3*2), speed=speed, connection=connection)
            self.rr = Leg(start_id=start_id+(3*3), speed=speed, inverted=True, connection=connection)
            self.all = Group([self.fl, self.fr, self.rl, self.rr])
            self.left = Group([self.fl, self.rl])
            self.right = Group([self.fr, self.rr])
            self.front = Group([self.fl, self.fr])
            self.rear = Group([self.rl, self.rr])

legs = Legs(connection=connection, speed=100, start_id=2)


legs.all.knee.goto(25)



# movement_speed = 300
# sc.goto(4, 95, movement_speed, True)

"""
# stand
sc.goto(2, -60, movement_speed, True)
sc.goto(3, 60, movement_speed, True)
sc.goto(4, -30, movement_speed, True)

sc.goto(5, 60, movement_speed, True)
sc.goto(6, -60, movement_speed, True)
sc.goto(7, 30, movement_speed, True)

sc.goto(8, -60, movement_speed, True)
sc.goto(9, 60, movement_speed, True)
sc.goto(10, -30, movement_speed, True)

sc.goto(11, 60, movement_speed, True)
sc.goto(12, -60, movement_speed, True)
sc.goto(13, 30, movement_speed, True)

# wait
time.sleep(3)

# rest
sc.goto(2, 45, movement_speed, True)
sc.goto(3, 90, movement_speed, True)
sc.goto(4, -90, movement_speed, True)

sc.goto(5, -45, movement_speed, True)
sc.goto(6, -90, movement_speed, True)
sc.goto(7, 90, movement_speed, True)

sc.goto(8, 45, movement_speed, True)
sc.goto(9, 90, movement_speed, True)
sc.goto(10, -90, movement_speed, True)

sc.goto(11, -45, movement_speed, True)
sc.goto(12, -90, movement_speed, True)
sc.goto(13, 90, movement_speed, True)
"""
