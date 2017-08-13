from pyax12.connection import Connection

sc = Connection(port='/dev/ttyACM0', baudrate=1000000)

ids = sc.scan()
print('you have', len(ids), 'servos connected')

for id in ids:
    sc.pretty_print_control_table(id)

sc.close()
