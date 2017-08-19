from pyax12.connection import Connection

sc = Connection(port='/dev/ttyACM0', baudrate=1000000)

print('will change id of #1 to next available id')
print('scanning...')

ids = sc.scan()
print('you have', len(ids), 'servos connected')

if 1 in ids:
    for next_available in range(2, 254):
        if not next_available in ids:
            break

    if next_available < 254:
        print('id', next_available, 'available')
        sc.set_id(1, next_available)
        print('done')
    else:
        print('no available servo ids')

else:
    print('no servo on id 1')

sc.close()
