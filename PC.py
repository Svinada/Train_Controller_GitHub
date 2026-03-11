import json
import socket
import time
import select
import configparser
import pynput
import os

sock = socket.socket()
port = 9600

image = ''
imagenew = 'DE2'
freq = 30
type = 0
usedisp = 1
usehost = 1
usebut = 1
maxvalues = {}
data = 0
line = 0
flag = ''
clients = 1

thrbutup = ''
thrbutdown = ''
brkbutup = ''
brkbutdown = ''
brklocbutup = ''
brklocbutdown = ''
revbutup = ''
revbutdown = ''
sandbut = ''

reverse = 0
thrust = 0
brake = 0
brakeloc = 0
sand = 0
but = 0

config = configparser.ConfigParser()
debug = 0

def sentphoto():
    global image, imagenew
    if usedisp == 1:
        if image != imagenew:
            if len(image) < 256:
                image = imagenew
                con.send(bytes(f'{image}', encoding="utf-8"))
                print('Sent photo:', image)
                return 0
            else:
                print('Cannot initialize photo - too much symbols')
                con.send(bytes('None', encoding="utf-8"))
                return 1

def getinfo():
    global data, line, flag, reverse, thrust, brake, brakeloc, sand
    data = con.recv(180).decode('utf-8')
    print(data)
    while '\n' in data:
        line, data = data.split('\n', 1)
        if not line:
            continue
        try:
            line = json.loads(line)
            reverse = line['rev']
            thrust = line['thr']
            brake = line['brk']
            brakeloc = line['brkloc']
            sand = line['sand']
        except json.decoder.JSONDecodeError as e:
            print('JSON Decode Error:', e)
        except Exception as e:
            print('Error:', e)

def configsetup():
    global imagenew, port, freq, type, usedisp, usehost, usebut, clients
    global thrbutup, thrbutdown, brkbutup, brkbutdown, brklocbutup, brklocbutup, revbutup, revbutdown, sandbut
    config.read('config.ini')
    if os.path.exists('config.ini'):
        defgame = config['HOST']['DefaultGame']
        port = int(config['NETWORK']['Port'])
        clients = int(config['NETWORK']['ClientsNumber'])
        imagenew = config['EV3']['DefaultImage']
        freq = int(config['EV3']['Frequency'])
        type = int(config['EV3']['Type'])
        usedisp = int(config['EV3']['UseDisp'])
        usehost = int(config['EV3']['UseHost'])
        usebut = int(config['EV3']['UseBut'])
        thrbutup = config['GAME_BINDS'][f'{defgame}.thrustup']
        thrbutdown = config['GAME_BINDS'][f'{defgame}.thrustdown']
        brkbutup = config['GAME_BINDS'][f'{defgame}.trainbrakeup']
        brkbutdown = config['GAME_BINDS'][f'{defgame}.trainbrakedown']
        brklocbutup = config['GAME_BINDS'][f'{defgame}.locbrakeup']
        brklocbutdown = config['GAME_BINDS'][f'{defgame}.locbrakedown']
        revbutup = config['GAME_BINDS'][f'{defgame}.reverseup']
        revbutdown = config['GAME_BINDS'][f'{defgame}.reversedown']
        sandbut = config['GAME_BINDS'][f'{defgame}.sand']
    else:
        print('No config file, creating new')
        defgame = input('Default game name WITHOUT spaces: ')
        config['HOST'] = {'DefaultGame': defgame}
        config['NETWORK'] = {
            'ClientsNumber': input('Max of clients number: '),
            'Port': input('Port number (better to use > 3000): '),
        }
        config['EV3'] = {
            'DefaultImage': input('Default image name WITHOUT spaces: '),
            'Frequency': input('Frequency in Hertz, pls dont use 0 ;) in range 0-127: '),
            'Type': input('Type of data: 0 - in %, 1 - in numbers: '),
            'UseDisp': input('Use display 1/0: '),
            'UseHost': input('Nothing 0/1: '),
            'UseBut': input('Use buttons on microcomputer 0/1: '),
        }
        config['GAME_BINDS'] = {
            f'{defgame}.thrustup': input('Button to thrust up: '),
            f'{defgame}.thrustdown': input('Button to thrust down: '),
            f'{defgame}.trainbrakeup': input('Button to train brake: '),
            f'{defgame}.trainbrakedown': input('Button to train brakedown: '),
            f'{defgame}.locbrakeup': input('Button to locbrake: '),
            f'{defgame}.locbrakedown': input('Button to locbrakedown: '),
            f'{defgame}.reverseup': input('Button to reverse up: '),
            f'{defgame}.reversedown': input('Button to reverse down: '),
            f'{defgame}.sand': input('Button to enable sand: '),
        }
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print('Config file created')


sock.bind(("", port))
sock.listen(clients)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

configsetup()
con.sendall(json.dumps({'freq': freq,'type': type,'usedisp': usedisp,'usehost': usehost,'usebut': usebut}).encode('utf-8'))

while flag != 'ready':
    flag = con.recv(32).decode('utf-8')
    print(flag)

if type == 1:
    maxvalues = json.loads(con.recv(1024).decode('utf-8'))
    print("maxvalues: ", maxvalues)
    while True:
        print('TODO')
        exit()
while True:
    sentphoto()
    getinfo()
    print(reverse, thrust, brake, brakeloc, sand)
    time.sleep(0.001)
