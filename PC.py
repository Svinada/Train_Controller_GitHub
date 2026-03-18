import json
import socket
import time
import select
import configparser
from pynput.keyboard import Key, Controller
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
flag = ''
clients = 1
trains = []
trainscount = 0

thrbutup = ''
thrbutdown = ''
brkbutup = ''
brkbutdown = ''
brklocbutup = ''
brklocbutdown = ''
revbutup = ''
revbutdown = ''
sandbut = ''

thrpos = 0
brkpos = 0
brklocpos = 0
sandpos = 0
deftrain = 0

reverse = 0
thrust = 0
brake = 0
brakeloc = 0
sand = 0
but = 0
selected = 'DE2'
butrev = 0
butthr = 0
butbrk = 0
butbrkloc = 0
butsand = 0

keyboard = Controller()
config = configparser.ConfigParser()

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
    global data, flag, reverse, thrust, brake, brakeloc, sand
    data = con.recv(180).decode('utf-8')
    print(data)
    while '\n' in data:
        line, data = data.split('\n', 1)
        if not data:
            continue
        try:
            data = json.loads(line)
            reverse = data['rev']
            thrust = data['thr']
            brake = data['brk']
            brakeloc = data['brkloc']
            sand = data['sand']
        except json.decoder.JSONDecodeError as e:
            print('JSON Decode Error:', e)
        except Exception as e:
            print('Error:', e)

def configsetup():
    global imagenew, port, freq, type, usedisp, usehost, usebut, clients, trains, trainscount, deftrain
    global thrbutup, thrbutdown, brkbutup, brkbutdown, brklocbutup, brklocbutdown, revbutup, revbutdown, sandbut
    global thrpos, brkpos, brklocpos, sandpos
    config.read('config.ini')
    if os.path.exists('config.ini'):
        defgame = config['HOST']['DefaultGame']
        deftrain = config['LOCOMOTIVES'][f'{defgame}.deftrain']
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
        trainscount = config['LOCOMOTIVES'][f'{defgame}.trainscount']
        thrpos = config['LOCOMOTIVE_BINDS'][f'{defgame}.{deftrain}.thrposnum']
        brkpos = config['LOCOMOTIVE_BINDS'][f'{defgame}.{deftrain}.brkposnum']
        brklocpos = config['LOCOMOTIVE_BINDS'][f'{defgame}.{deftrain}.brklocposnum']
        sandpos = config['LOCOMOTIVE_BINDS'][f'{defgame}.{deftrain}.sandposnum']
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
        trainscount = input('Number of trains in game to add in config WITHOUT spaces: ')
        config['LOCOMOTIVES'] = {f'{defgame}.trainscount': trainscount}
        for i in range(1, int(trainscount) + 1):
            config.set('LOCOMOTIVES', f'{defgame}.{i}', input(f'Train {i}: '))
        i = 0
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print('Config file created')
    for i in range(1, int(trainscount) + 1):
        trains.append(config['LOCOMOTIVES'][f'{defgame}.{i}'])

def butpress():
    global reverse, thrust, brake, brakeloc, sand, trains, selected
    global butrev, butbrk, butbrkloc, butsand, butthr
    global thrbutup, thrbutdown, brkbutup, brkbutdown, brklocbutup, brklocbutdown, revbutup, revbutdown, sandbut
    if reverse != butrev:
        if reverse > butrev:
            for i in range(butrev, int(reverse)):
                keyboard.tap(revbutup)
        else:
            for i in range(reverse, int(butrev)):
                keyboard.tap(revbutdown)
        butrev = reverse
    thrdelta = round((int(thrpos) / 100) * thrust)
    if butthr != thrdelta:
        if thrdelta > butthr:
            for i in range(butthr, thrdelta):
                keyboard.tap(thrbutup)
        else:
            for i in range(thrdelta, butthr):
                keyboard.tap(thrbutdown)
        butthr = thrdelta
    brkdelta = round((int(brkpos) / 100) * brake)
    if butbrk != brkdelta:
        if brkdelta > butbrk:
            for i in range(butbrk, brkdelta):
                keyboard.tap(brkbutup)
        else:
            for i in range(brkdelta, butbrk):
                keyboard.tap(brkbutdown)
        butbrk = brkdelta
    brklocdelta = round((int(brklocpos) / 100) * brakeloc)
    if butbrkloc != brklocdelta:
        if brklocdelta > butbrkloc:
            for i in range(butbrkloc, brklocdelta):
                keyboard.tap(brklocbutup)
        else:
            for i in range(brklocdelta, butbrkloc):
                keyboard.tap(brklocbutdown)
        butbrkloc = brklocdelta

configsetup()

sock.bind(("", port))
sock.listen(clients)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

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
    butpress()
    print(reverse, thrust, brake, brakeloc, sand)
    time.sleep(0.001)

