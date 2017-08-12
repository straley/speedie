from pyax12.connection import Connection

sc = Connection(port='/dev/ttyACM0', baudrate=1000000)

sc.goto(2, -60, 100, True)
sc.goto(3, 60, 100, True)
sc.goto(4, -30, 100, True)

sc.goto(5, 60, 100, True)
sc.goto(6, -60, 100, True)
sc.goto(7, 30, 100, True)

sc.goto(8, -60, 100, True)
sc.goto(9, 60, 100, True)
sc.goto(10, -30, 100, True)

sc.goto(11, 60, 100, True)
sc.goto(12, -60, 100, True)
sc.goto(13, 30, 100, True)
