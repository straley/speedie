from robot.robot import Robot

speedie = Robot(speed=150)
try:
    speedie.stand()

    speedie.walk(4, "forward")
    speedie.walk(4, "backward")

    speedie.flat()


except ValueError:
    print("ValueError")

print("closing")
speedie.close()
