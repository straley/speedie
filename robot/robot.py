import time
from pyax12.connection import Connection
import pkg_resources

print("pyax12 version", pkg_resources.get_distribution("pyax12").version)

class Robot(object):
    def __init__(self, speed=150, port='/dev/ttyACM0', baudrate=1000000, start_id=2, debug=False):

        self.speed = speed
        self.connection = Connection(port=port, baudrate=baudrate)
        self.legs = Legs(connection=self.connection, speed=self.speed, start_id=start_id)
        self.debug = debug
        self.connection.flush()
        if (self.debug):
            print("[debug] connected to port", port, "at", baudrate, baudrate)

    def reset(self):
        if (self.debug):
            print("[debug] scanning")
        self.connection.scan()

        if (self.debug):
            print("[debug] ready")


    def close(self):
        self.connection.close()
        if (self.debug):
            print("[debug] closed")

    def stand(self):
        if (self.debug):
            print("[debug] stand")
        self.legs.all.hip.goto(45)
        self.legs.all.knee.goto(-60)
        self.legs.all.ankle.goto(-30)

    def kneel(self):
        if (self.debug):
            print("[debug] kneel")
        self.legs.all.hip.goto(-45)
        self.legs.all.knee.goto(-90)
        self.legs.all.ankle.goto(-90)

    def flat(self):
        if (self.debug):
            print("[debug] flat")
        self.legs.all.hip.goto(90)
        self.legs.all.knee.goto(0)
        self.legs.all.ankle.goto(0)

    def walk(self, steps=1, direction="forward", knee_up=False):
        if (self.debug):
            print("[debug] walk", direction, steps, "steps")

        if knee_up == False:
            walk = Walk(self)
        else:
            walk = Walk(self, knee_up=knee_up)

        for i in range(0,steps):
            walk.step_vertical(["fl", "rr"], "down")
            walk.step_horizontal("fl", "rl", direction)
            walk.step_horizontal("rr", "fl", direction)
            walk.step_vertical(["fl", "rr"], "up")
            walk.step_vertical(["fr", "rl"], "down")
            walk.step_horizontal("fr", "rr", direction)
            walk.step_horizontal("rl", "fr", direction)
            walk.step_vertical(["fr", "rl"], "up")


    def get_status(self):
        servos = [2,3,5,6,8,9,11,12]

        min_voltage = 999
        max_voltage = 0
        sum_voltage = 0
        good_count = 0

        for servo in servos:
            try:
                if not self.connection.ping(servo):
                    print("ping failed servo", servo)
                    
                voltage = self.connection.get_present_voltage(servo)
                if voltage > max_voltage:
                    max_voltage = voltage
                elif voltage < min_voltage:
                    min_voltage = voltage
                sum_voltage += voltage
                good_count = good_count + 1
            except:
                print ("[error] cannot connect to", servo)

        if good_count > 0:
            print (min_voltage, max_voltage, sum_voltage / good_count)
        else:
            print("no servos online")

class Joint(object):
    def __init__(self, id, inverted=False, min=-150, max=150, speed=False, connection=False):
        self.id = id
        self.inverted = inverted
        self.min = min
        self.max = max
        self._speed = speed
        self.connection = connection

    def get_load(self):
        return self.connection.get_present_load(self.id)

    def speed(self, value=False):
        self._speed = value

    def goto(self, position, speed=False):
        if position < self.min:
            position = self.min
        elif position > self.max:
            position = self.max

        if self.inverted:
            position = -position


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
        super(Knee, self).__init__(id=id, inverted=not inverted, min=-95, max=95, speed=speed, connection=connection)

class Hip(Joint):
    def __init__(self, id, inverted=False, speed=False, connection=False):
        super(Hip, self).__init__(id=id, inverted=not inverted, min=-60, max=95, speed=speed, connection=connection)

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

    def get_load(self):
        loads = [self.hip.get_load(), self.knee.get_load()] #[self.ankle.get_load()
        return {
            "min": min(loads),
            "max": max(loads),
            "avg": sum(loads)/len(loads)
        }

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
            self.rr = Leg(start_id=start_id, speed=speed, connection=connection)
            self.rl = Leg(start_id=start_id+3, speed=speed, inverted=True, connection=connection)
            self.fl = Leg(start_id=start_id+(3*2), speed=speed, connection=connection)
            self.fr = Leg(start_id=start_id+(3*3), speed=speed, inverted=True, connection=connection)
            self.all = Group([self.fl, self.fr, self.rl, self.rr])
            self.left = Group([self.fl, self.rl])
            self.right = Group([self.fr, self.rr])
            self.front = Group([self.fl, self.fr])
            self.rear = Group([self.rl, self.rr])


class Walk(object):
    def __init__(self, robot, step_delay=0.05, cycle_delay=0.01, hip_center=45, hip_offset=45, knee_up=-45, knee_down=0):
        self.robot = robot
        self.step_delay = step_delay
        self.cycle_delay = cycle_delay
        self.hip_center = hip_center
        self.hip_offset = hip_offset
        self.knee_up = knee_up
        self.knee_down = knee_down

    def step_vertical(self, legs, direction):
        for leg in legs:
            if leg in dir(self.robot.legs):
                if direction == "up":
                    getattr(self.robot.legs, leg).knee.goto(self.knee_up)
                    getattr(self.robot.legs, leg).ankle.goto(-90-self.knee_up)
                elif direction == "down":
                    getattr(self.robot.legs, leg).knee.goto(self.knee_down)
                    getattr(self.robot.legs, leg).ankle.goto(-90-self.knee_down)

            time.sleep(self.cycle_delay)

        if self.step_delay > self.cycle_delay:
            time.sleep(self.step_delay - self.cycle_delay)

    def step_horizontal(self, lead_leg, trailing_leg, direction):
        if lead_leg in dir(self.robot.legs) and trailing_leg in dir(self.robot.legs):
            if direction == "forward":
                getattr(self.robot.legs, lead_leg).hip.goto(self.hip_center + self.hip_offset)
                time.sleep(self.cycle_delay)
                getattr(self.robot.legs, trailing_leg).hip.goto(self.hip_center)
                time.sleep(self.cycle_delay)
            elif direction == "backward":
                getattr(self.robot.legs, lead_leg).hip.goto(self.hip_center - self.hip_offset)
                time.sleep(self.cycle_delay)
                getattr(self.robot.legs, trailing_leg).hip.goto(self.hip_center)
                time.sleep(self.cycle_delay)
