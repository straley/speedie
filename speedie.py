import time
from robot.robot import Robot

speedie = Robot(speed=150, debug=True)

# speedie.get_status()

for i in range(0,1000):
    # speedie.stand()
    speedie.get_status()
    # time.sleep(1)
    # speedie.get_status()
    #speedie.kneel()
    # time.sleep(1)
    # speedie.get_status()



print("closing")
speedie.close()
