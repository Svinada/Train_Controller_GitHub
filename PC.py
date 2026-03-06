import json
import socket
import time
import select

sock = socket.socket()
port = 9600

image = ''
imagenew = 'DE2'
freq = 30
type = 0
usedisp = 1
usehost = 1
usebut = 1
minvalues = {}

data = 0
reverse = 0
thrust = 0
brake = 0
brakeloc = 0
sand = 0
but = 0

debug = 1

if debug == True:
    freq = int(input("Frequency in range 0-127"))
    if freq < 0 or freq > 127:
        freq = int(input("Wrong frequency, write value in range 0-127"))
    type = int(input("Type of data: 0 - in %, 1 - in numbers"))
    if type < 0 or type > 1:
        type = int(input("Wrong type, use 0-1"))
    usedisp = int(input("Use display (doesn't replace brickman) 0/1"))
    if usedisp < 0 or usedisp > 1:
        usedisp = int(input("Wrong value of use display, use 0/1"))
    usehost = int(input("Nothing 0/1"))
    if usehost < 0 or usehost > 1:
        usehost = int(input("Nothing, use 0/1"))
    usebut = int(input("Use buttons on microcomputer 0/1"))
    if usebut < 0 or usebut > 1:
        usebut = int(input("Wrong value of using buttons, use 0/1"))

print(freq, type, usedisp, usehost, usebut)

config = {'freq': freq,
          'type': type,
          'usedisp': usedisp,
          'usehost': usehost,
          'usebut': usebut}
print('config:', config)
config = json.dumps(config)

sock.bind(("", port))
sock.listen(1)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

con.send(config.encode('utf-8'))
if type == 1:
    minvalues = json.loads(con.recv(1024).decode('utf-8'))
    while True:
        print('TODO')
        exit()
else:
    while True:
        if usedisp == 1:
            if image != imagenew:
                if len(image) < 256:
                    image = imagenew
                    con.send(bytes(f'{image}', encoding="utf-8"))
                else:
                    print('Cannot initialize photo - too much symbols')
                    con.send(bytes('None', encoding="utf-8"))
        data = json.loads(con.recv(1024).decode('utf-8'))
        print(data)
        reverse = data['rev']
        thrust = data['thr']
        brake = data['brk']
        brakeloc = data['brkloc']
        sand = data['sand']
        print(reverse, thrust, brake, brakeloc, sand)
        time.sleep(0.001)