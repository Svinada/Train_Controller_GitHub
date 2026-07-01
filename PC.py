import json
import socket
import time
import select
import configparser
import pyautogui as keyboard # noqa
import os

from TrainControllerV2 import frequency

image = ''
maximum_values = {}
ready_flag = ''
trains = []
sand_counter = 0
but_press_delay = 0.1
but_timeout = 0
counter = 0
setup_1 = 0
setup_2 = 0

#maybe under comm
thrust_button_up = ''
thrust_button_down = ''
brake_button_up = ''
brake_button_down = ''
brake_locomotive_button_up = ''
brake_locomotive_button_down = ''
reverse_button_up = ''
reverse_button_down = ''
sand_button_up = ''
sand_button_down = ''

selected = 'DE2'

reverse_raw = 0
thrust_raw = 0
brake_raw = 0
brake_locomotive_raw = 0
sand_raw = 0
button_left_raw = 0
button_up_raw = 0
button_right_raw = 0
button_down_raw = 0

reverse_data = 0 #All ..._data variables provided as a percentage
thrust_data = 0
brake_data = 0
brake_locomotive_data = 0
sand_data = 0
button_left_data = 0
button_up_data = 0
button_right_data = 0
button_down_data = 0

config = configparser.ConfigParser()
sock = socket.socket()

def sentphoto():
    global image
    if usedisp == 1:
        if image != selected:
            image = selected
            con.send(bytes(f'{image}', encoding="utf-8"))
            print('Sent photo:', image)

def getinfo():
    global data, ready_flag, reverse_raw, thrust_raw, brake_raw, brake_locomotive_raw, sand_raw, button_left_raw, button_up_raw, button_right_raw, button_down_raw
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
            brake_locomotive_raw = int(data['brkloc'])
            sand_raw = int(data['sand'])
            button_left_raw = int(data['butleft'])
            button_up_raw = int(data['butup'])
            button_right_raw = int(data['butright'])
            button_down_raw = int(data['butdown'])
        except json.decoder.JSONDecodeError as e:
            print('JSON Decode Error:', e, 'JSON data:', '\n' + data)
        except Exception as e:
            print('Error:', e, 'JSON data:', '\n' + data)

def configupdate():
    global default_game, thrust_button_up, thrust_button_down, brake_button_up, brake_button_down, brake_locomotive_button_up, brake_locomotive_button_down, reverse_button_up, reverse_button_down, sand_button_up, sand_button_down
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, default_train
    thrust_button_up = config[f'{default_game}.GAME_BINDS']['thrustup']
    thrust_button_down = config[f'{default_game}.GAME_BINDS']['thrustdown']
    brake_button_up = config[f'{default_game}.GAME_BINDS']['trainbrakeup']
    brake_button_down = config[f'{default_game}.GAME_BINDS']['trainbrakedown']
    brake_locomotive_button_up = config[f'{default_game}.GAME_BINDS']['locbrakeup']
    brake_locomotive_button_down = config[f'{default_game}.GAME_BINDS']['locbrakedown']
    reverse_button_up = config[f'{default_game}.GAME_BINDS']['reverseup']
    reverse_button_down = config[f'{default_game}.GAME_BINDS']['reversedown']
    sand_button_up = config[f'{default_game}.GAME_BINDS']['sandup']
    sand_button_down = config[f'{default_game}.GAME_BINDS']['sanddown']
    thrust_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{selected}.thrposnum'])
    brake_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{selected}.brkposnum'])
    brakeloc_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{selected}.brklocposnum'])
    sand_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{selected}.sandposnum'])
    print('selected:', selected, 'brake_pos:', brake_pos,'brakeloc_pos:', brakeloc_pos, 'thrust_pos:', thrust_pos,'sand_pos:', sand_pos)

def configsetup():
    global default_game, port, clients_number, frequency, type, usedisp, game_profile_type
    if os.path.exists('config.ini'):
        config.read('config.ini')
        default_game = config['HOST']['DefaultGame']
        port = int(config['NETWORK']['Port'])
        clients_number = int(config['NETWORK']['ClientsNumber'])
        frequency = int(config['EV3']['Frequency'])
        type = int(config['EV3']['Type'])
        usedisp = int(config['EV3']['UseDisp'])

        if os.path.exists('game profiles'):
            if game_profile_type == 0 and os.path.exists('game profiles/config.ini'):

        else:
            print('directory "game profiles" not found')
        # thrust_button_up = config[f'{default_game}.GAME_BINDS']['thrustup']
        # thrust_button_down = config[f'{default_game}.GAME_BINDS']['thrustdown']
        # brake_button_up = config[f'{default_game}.GAME_BINDS']['trainbrakeup']
        # brake_button_down = config[f'{default_game}.GAME_BINDS']['trainbrakedown']
        # brake_locomotive_button_up = config[f'{default_game}.GAME_BINDS']['locbrakeup']
        # brake_locomotive_button_down = config[f'{default_game}.GAME_BINDS']['locbrakedown']
        # reverse_button_up = config[f'{default_game}.GAME_BINDS']['reverseup']
        # reverse_button_down = config[f'{default_game}.GAME_BINDS']['reversedown']
        # sand_button_up = config[f'{default_game}.GAME_BINDS']['sandup']
        # sand_button_down = config[f'{default_game}.GAME_BINDS']['sanddown']
        # trains_count = int(config[f'{default_game}.LOCOMOTIVES']['trainscount'])
        # thrust_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{default_train}.thrposnum'])
        # brake_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{default_train}.brkposnum'])
        # brakeloc_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{default_train}.brklocposnum'])
        # sand_pos = int(config[f'{default_game}.LOCOMOTIVE_CONFIG'][f'{default_train}.sandposnum'])
    else:
        configcreate()

def configcreate():
    global default_game, clients_number, port, frequency, game_profiles_counter, game_profile_type
    print('No config file, creating new')
    default_game = input('Enter default game: ')
    clients_number = int(input('Enter number of clients: '))
    port = int(input('Enter port: '))
    frequency = int(input('Enter frequency: '))
    game_profiles_counter = int(input('Enter number of game profiles: '))
    try:
        if os.path.exists('game profiles'):
            print('folder game profiles already exists')
        os.mkdir('game profiles')
        print('created "game profiles" folder in script folder')
    except Exception as e:
        print('Cannot create folder:', e)
    config['HOST'] = {
        'default_game': default_game,
    }
    config['NETWORK'] = {
        'port': str(port),
        'clients_number': str(clients_number)
    }
    config['EV3'] = {
        'frequency': str(frequency)
    }
    config['GAME_PROFILES'] = {
        'game_profiles_counter': str(game_profiles_counter)
    }
    for i in range(1, game_profiles_counter + 1):
        config['GAME_PROFILES'] = {
            f'game_name.{i}': input(f'Enter game name {i}: '),
            f'game_profile_type.{i}': input(f'Enter game profile type {i}: '),
        }
    game_profile_type = config['GAME_PROFILES']['game_profile_type.1']
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    print('Config created, remember to config game profile before starting program')

def butpress():
    global trains, selected, sand_counter, but_timeout
    global reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data, button_left_data, button_up_data, button_right_data, button_down_data

    if reverse_raw != reverse_data:
        if reverse_raw > reverse_data:
            for i in range(reverse_data, reverse_raw):
                keyboard.press(reverse_button_up)
                time.sleep(but_press_delay)
        else:
            for i in range(reverse_raw, reverse_data):
                keyboard.press(reverse_button_down)
                time.sleep(but_press_delay)
        reverse_data = reverse_raw

    if but_timeout == 0:
        thrdelta = round((thrust_pos / 100) * thrust_raw)
        if thrust_data != thrdelta:
            if thrdelta > thrust_data:
                thrust_data += 1
                keyboard.press(thrust_button_up)
            else:
                thrust_data -= 1
                keyboard.press(thrust_button_down)
            but_timeout = 1

        brkdelta = round((brake_pos / 100) * brake_raw)
        if brake_data != brkdelta:
            if brkdelta > brake_data:
                brake_data += 1
                keyboard.press(brake_button_up)
            else:
                brake_data -= 1
                keyboard.press(brake_button_down)
            but_timeout = 1

        brklocdelta = round((brakeloc_pos / 100) * brake_locomotive_raw)
        if brake_locomotive_data != brklocdelta:
            if brklocdelta > brake_locomotive_data:
                brake_locomotive_data += 1
                keyboard.press(brake_locomotive_button_up)
            else:
                brake_locomotive_data -= 1
                keyboard.press(brake_locomotive_button_down)
            but_timeout = 1

    if sand_raw != sand_data:
        sand_data = sand_raw
        if sand_data == 0:
            sand_counter = sand_counter + 1
            if sand_counter > sand_pos:
                sand_counter = 0
                for i in range(sand_pos): #That's bad I know
                    keyboard.press(sand_button_down)
                    time.sleep(but_press_delay)
            else:
                keyboard.press(sand_button_up)

    if button_right_raw != button_right_data:
        button_right_data = button_right_raw
        if button_right_data == 0:
            if len(trains) < trains.index(selected) + 2:
                selected = trains[0]
            else:
                selected = trains[trains.index(selected) + 1]
            configupdate()

    if button_left_raw != button_left_data:
        button_left_data = button_left_raw
        if button_left_data == 0:
            if trains.index(selected) == 0:
                selected = trains[len(trains) - 1]
            else:
                selected = trains[trains.index(selected) - 1]
            configupdate()

configsetup()

sock.bind(("", port))
sock.listen(clients_number)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

con.sendall(json.dumps({'freq': frequency,'type': type,'usedisp': usedisp,'usehost': setup_1,'usebut': setup_2}).encode('utf-8'))

while ready_flag != 'ready':
    ready_flag = con.recv(32).decode('utf-8')
    print(ready_flag)


# if type == 1:
#     maximum_values = json.loads(con.recv(1024).decode('utf-8'))
#     print("maxvalues: ", maximum_values)
#     while True:

while True:
    if but_timeout == 1:
        counter += 1
        if counter >= 5:
            counter = 0
            but_timeout = 0
    sentphoto()
    getinfo()
    butpress()
    # print(reverse_raw, thrust_raw, brake_raw, brake_locomotive_raw, sand_raw)
    time.sleep(0.01)

