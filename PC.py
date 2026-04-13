import json
import socket
import time
import select
import configparser
import pyautogui as keyboard # noqa
import os

sock = socket.socket()

image = ''
imagenew = 'DE2'
maxvalues = {}
flag = ''
trains = []
sand_counter = 0
but_press_delay = 0.01

# type = 0
# usedisp = 1
# usehost = 1
# usebut = 1
# clients = 1
# trains_count = 0
# port = 9600

#maybe under comm
thrbutup = ''
thrbutdown = ''
brkbutup = ''
brkbutdown = ''
brklocbutup = ''
brklocbutdown = ''
revbutup = ''
revbutdown = ''
sandbutup = ''
sandbutdown = ''


# thrust_pos = 0 position of thrust !!! All - 1 = pos !!!
# brake_pos = 0
# brakeloc_pos = 0
# sand_pos = 0
# defalt_train = 0

selected = 'DE2'

reverse_raw = 0
thrust_raw = 0
brake_raw = 0
brakeloc_raw = 0
sand_raw = 0
butleft_raw = 0
butup_raw = 0
butright_raw = 0
butdown_raw = 0

reverse_data = 0
thrust_data = 0
brake_data = 0
brakeloc_data = 0
sand_data = 0
butleft_data = 0
butup_data = 0
butright_data = 0
butdown_data = 0

config = configparser.ConfigParser()

def sentphoto():
    global image
    if usedisp == 1:
        if image != selected:
            image = selected
            con.send(bytes(f'{image}', encoding="utf-8"))
            print('Sent photo:', image)

def getinfo():
    global data, flag, reverse_raw, thrust_raw, brake_raw, brakeloc_raw, sand_raw, butleft_raw, butup_raw, butright_raw, butdown_raw
    data = con.recv(1024).decode('utf-8')
    # print(data)
    a = 0
    while '\n' in data:
        a = a + 1
        if a == 3:
            continue
        line, data = data.split('\n', 1)
        try:
            data = json.loads(line)
            reverse_raw = int(data['rev'])
            thrust_raw = int(data['thr'])
            brake_raw = int(data['brk'])
            brakeloc_raw = int(data['brkloc'])
            sand_raw = int(data['sand'])
            butleft_raw = int(data['butleft'])
            butup_raw = int(data['butup'])
            butright_raw = int(data['butright'])
            butdown_raw = int(data['butdown'])
        except json.decoder.JSONDecodeError as e:
            print('JSON Decode Error:', e, 'JSON data:', '\n' + data)
        except Exception as e:
            print('Error:', e, 'JSON data:', '\n' + data)

def configupdate():
    global defgame, thrbutup, thrbutdown, brkbutup, brkbutdown, brklocbutup, brklocbutdown, revbutup, revbutdown, sandbutup, sandbutdown
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, default_train
    default_train = selected
    thrbutup = config['GAME_BINDS'][f'{defgame}.thrustup']
    thrbutdown = config['GAME_BINDS'][f'{defgame}.thrustdown']
    brkbutup = config['GAME_BINDS'][f'{defgame}.trainbrakeup']
    brkbutdown = config['GAME_BINDS'][f'{defgame}.trainbrakedown']
    brklocbutup = config['GAME_BINDS'][f'{defgame}.locbrakeup']
    brklocbutdown = config['GAME_BINDS'][f'{defgame}.locbrakedown']
    revbutup = config['GAME_BINDS'][f'{defgame}.reverseup']
    revbutdown = config['GAME_BINDS'][f'{defgame}.reversedown']
    sandbutup = config['GAME_BINDS'][f'{defgame}.sandup']
    sandbutdown = config['GAME_BINDS'][f'{defgame}.sanddown']
    thrust_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.thrposnum'])
    brake_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.brkposnum'])
    brakeloc_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.brklocposnum'])
    sand_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.sandposnum'])

def configsetup():
    global imagenew, port, freq, type, usedisp, usehost, usebut, clients, trains, trains_count, defalt_train, defgame
    global thrbutup, thrbutdown, brkbutup, brkbutdown, brklocbutup, brklocbutdown, revbutup, revbutdown, sandbutup, sandbutdown
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos
    config.read('config.ini')
    if os.path.exists('config.ini'):
        defgame = config['HOST']['DefaultGame']
        defalt_train = config['LOCOMOTIVES'][f'{defgame}.deftrain']
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
        sandbutup = config['GAME_BINDS'][f'{defgame}.sandup']
        sandbutdown = config['GAME_BINDS'][f'{defgame}.sanddown']
        trains_count = int(config['LOCOMOTIVES'][f'{defgame}.trainscount'])
        thrust_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.thrposnum'])
        brake_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.brkposnum'])
        brakeloc_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.brklocposnum'])
        sand_pos = int(config['LOCOMOTIVE_BINDS'][f'{defgame}.{defalt_train}.sandposnum'])
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
            f'{defgame}.sandup': input('Button to sand up: '),
            f'{defgame}.sanddown': input('Button to sand down: '),
        }
        trains_count = input('Number of trains in game to add in config WITHOUT spaces: ')
        config['LOCOMOTIVES'] = {f'{defgame}.trainscount': trains_count}
        for i in range(1, int(trains_count) + 1):
            config.set('LOCOMOTIVES', f'{defgame}.{i}', input(f'Train {i}: '))
        i = 0
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print('Config file created')
    for i in range(1, int(trains_count) + 1):
        trains.append(config['LOCOMOTIVES'][f'{defgame}.{i}'])

def butpress():
    global trains, selected, sand_counter
    global reverse_data, brake_data, brakeloc_data, sand_data, thrust_data, butleft_data, butup_data, butright_data, butdown_data

    if reverse_raw != reverse_data:
        if reverse_raw > reverse_data:
            for i in range(reverse_data, reverse_raw):
                keyboard.press(revbutup)
                time.sleep(but_press_delay)
        else:
            for i in range(reverse_raw, reverse_data):
                keyboard.press(revbutdown)
                time.sleep(but_press_delay)
        reverse_data = reverse_raw

    thrdelta = round((thrust_pos / 100) * thrust_raw)
    if thrust_data != thrdelta:
        if thrdelta > thrust_data:
            for i in range(thrust_data, thrdelta):
                keyboard.press(thrbutup)
                time.sleep(but_press_delay)
        else:
            for i in range(thrdelta, thrust_data):
                keyboard.press(thrbutdown)
                time.sleep(but_press_delay)
        thrust_data = thrdelta

    brkdelta = round((brake_pos / 100) * brake_raw)
    if brake_data != brkdelta:
        if brkdelta > brake_data:
            for i in range(brake_data, brkdelta):
                keyboard.press(brkbutup)
                time.sleep(but_press_delay)
        else:
            for i in range(brkdelta, brake_data):
                keyboard.press(brkbutdown)
                time.sleep(but_press_delay)
        brake_data = brkdelta

    brklocdelta = round((brakeloc_pos / 100) * brakeloc_raw)
    if brakeloc_data != brklocdelta:
        if brklocdelta > brakeloc_data:
            for i in range(brakeloc_data, brklocdelta):
                keyboard.press(brklocbutup)
                time.sleep(but_press_delay)
        else:
            for i in range(brklocdelta, brakeloc_data):
                keyboard.press(brklocbutdown)
                time.sleep(but_press_delay)
        brakeloc_data = brklocdelta

    if sand_raw != sand_data:
        sand_data = sand_raw
        if sand_data == 0:
            sand_counter = sand_counter + 1
            if sand_counter > sand_pos:
                sand_counter = 0
                for i in range(sand_pos):
                    keyboard.press(sandbutdown)
                    time.sleep(but_press_delay)
            else:
                keyboard.press(sandbutup)

    if butright_raw != butright_data:
        butright_data = butright_raw
        if butright_data == 0:
            if len(trains) < trains.index(selected) + 2:
                selected = trains[0]
            else:
                selected = trains[trains.index(selected) + 1]
            configupdate()

    if butleft_raw != butleft_data:
        butleft_data = butleft_raw
        if butleft_data == 0:
            if trains.index(selected) == 0:
                selected = trains[len(trains) - 1]
            else:
                selected = trains[trains.index(selected) - 1]
            configupdate()

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


# if type == 1:
#     maxvalues = json.loads(con.recv(1024).decode('utf-8'))
#     print("maxvalues: ", maxvalues)
#     while True:

while True:
    sentphoto()
    getinfo()
    butpress()
    # print(reverse_raw, thrust_raw, brake_raw, brakeloc_raw, sand_raw)
    time.sleep(0.01)

