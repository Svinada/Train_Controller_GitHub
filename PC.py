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
config = 0

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

config = freq << 1
config = (config | type) << 1
config = (config | usedisp) << 1
config = (config | usehost) << 1
config = config | usebut

# config = config.to_bytes((config.bit_length() + 7) // 8, 'big')
config = config.to_bytes(2, byteorder="big")
print(config)
print(int.from_bytes(config, "big"))

sock.bind(("", port))
sock.listen(1)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

con.send(config)
while True:
    if usedisp == 1:
        if image != imagenew:
            if len(image) < 256:
                con.send(bytes(f'{image}', encoding="utf-8"))
            else:
                print('Cannot initialize photo - too much symbols')
                con.send(bytes('None', encoding="utf-8"))
    data = con.recv(4)
    data = int.from_bytes(data, byteorder="big")
    print(bin(data))
    sand = data & 1
    brakeloc = (data >> 1) & 127
    brake = (data >> 8) & 127
    thrust = (data >> 15) & 127
    reverse = (data >> 22) & 3
    print(reverse, thrust, brake, brakeloc, sand)
    time.sleep(0.001)