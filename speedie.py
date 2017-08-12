import time

from pyax12.connection import Connection
from robot.body import Legs

connection = Connection(port='/dev/ttyACM0', baudrate=1000000)
legs = Legs(connection=connection, speed=150, start_id=2)


# stand
legs.all.hip.goto(-45)
legs.all.knee.goto(-60)
legs.all.ankle.goto(-30)

# wait
time.sleep(3)

# kneel
legs.all.hip.goto(45)
legs.all.knee.goto(-90)
legs.all.ankle.goto(-90)

# wait
time.sleep(3)

# rest
legs.all.hip.goto(-90)
legs.all.knee.goto(0)
legs.all.ankle.goto(0)
