import json
import sys
import socket
import time
import select
import configparser
from pynput.keyboard import Key, Controller
import os
import importlib

image = ''
maximum_values = {}
ready_flag = ''
trains = []
sand_counter = 0
but_press_delay = 0.1
but_timeout_flag = 0
but_timeout_timer = 5
counter = 0
setup_1 = 0
setup_2 = 0
game_profile_selecting_flag = 0
usedisp = 1

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

# selected_locomotive = 'DE2'

reverse_raw = 0
thrust_raw = 0
brake_raw = 0
brake_locomotive_raw = 0
sand_raw = 0
button_left_raw = 0
button_up_raw = 0
button_right_raw = 0
button_down_raw = 0

reverse_data = 0 #All ..._raw variables provided as a percentage (0-100%)
thrust_data = 0 #All ..._data variables provided as a current position
brake_data = 0
brake_locomotive_data = 0
sand_data = 0
button_left_data = 0
button_up_data = 0
button_right_data = 0
button_down_data = 0

config = configparser.ConfigParser()
sock = socket.socket()
keyboard = Controller()

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def sentphoto(a = ''):
    global image
    if usedisp == 1:
        if game_profile_selecting_flag == 0:
            if image != selected_locomotive:
                image = selected_locomotive
                con.send(bytes(f'{image}', encoding="utf-8"))
                print('Sent photo:', image)
        else:
            if image != a:
                image = a
                con.send(bytes(f'{'\t'+a}', encoding="utf-8"))
                print('Sent text:', a)

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
    global default_game_name, thrust_button_up, thrust_button_down, brake_button_up, brake_button_down, brake_locomotive_button_up, brake_locomotive_button_down, reverse_button_up, reverse_button_down, sand_button_up, sand_button_down
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, selected_locomotive, ButConfig, game_profile_type, locomotives_count, selected_locomotive_number, but_timeout_timer
    if game_profile_selecting_flag == 0:
        if game_profile_type == 0:
            if os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini')):
                config.read(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini'))
            else:
                print('config not found with name', default_game_name)
                configcreate()
            selected_locomotive = config['LOCOMOTIVES'][str(selected_locomotive_number)]
            thrust_button_up = config[selected_locomotive]['thrust_button_up']
            thrust_button_down = config[selected_locomotive]['thrust_button_down']
            brake_button_up = config[selected_locomotive]['brake_button_up']
            brake_button_down = config[selected_locomotive]['brake_button_down']
            brake_locomotive_button_up = config[selected_locomotive]['brake_locomotive_button_up']
            brake_locomotive_button_down = config[selected_locomotive]['brake_locomotive_button_down']
            reverse_button_up = config[selected_locomotive]['reverse_button_up']
            reverse_button_down = config[selected_locomotive]['reverse_button_down']
            sand_button_up = config[selected_locomotive]['sand_button_up']
            sand_button_down = config[selected_locomotive]['sand_button_down']
            thrust_pos = int(config[selected_locomotive]['thrust_position_number'])
            brake_pos = int(config[selected_locomotive]['brake_position_number'])
            brakeloc_pos = int(config[selected_locomotive]['brake_locomotive_position_number'])
            sand_pos = int(config[selected_locomotive]['sand_position_number'])
        else:
            print('.py profile running, locomotive changed')
    else:
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
        game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
        if game_profile_type == 0:
            if os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini')):
                config.read(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini'))
            else:
                print('config not found with name', default_game_name)
                configcreate()
            locomotives_count = int(config['LOCOMOTIVES']['locomotives_count'])
            selected_locomotive_number = 1
            selected_locomotive = config['LOCOMOTIVES'][str(selected_locomotive_number)]
            thrust_button_up = config[selected_locomotive]['thrust_button_up']
            thrust_button_down = config[selected_locomotive]['thrust_button_down']
            brake_button_up = config[selected_locomotive]['brake_button_up']
            brake_button_down = config[selected_locomotive]['brake_button_down']
            brake_locomotive_button_up = config[selected_locomotive]['brake_locomotive_button_up']
            brake_locomotive_button_down = config[selected_locomotive]['brake_locomotive_button_down']
            reverse_button_up = config[selected_locomotive]['reverse_button_up']
            reverse_button_down = config[selected_locomotive]['reverse_button_down']
            sand_button_up = config[selected_locomotive]['sand_button_up']
            sand_button_down = config[selected_locomotive]['sand_button_down']
            thrust_pos = int(config[selected_locomotive]['thrust_position_number'])
            brake_pos = int(config[selected_locomotive]['brake_position_number'])
            brakeloc_pos = int(config[selected_locomotive]['brake_locomotive_position_number'])
            sand_pos = int(config[selected_locomotive]['sand_position_number'])
        if game_profile_type == 1:
            ButConfig = importlib.import_module(f'game_profiles.{default_game_name}')
            but_timeout_timer = ButConfig.but_timeout_timer
            locomotives_count = ButConfig.locomotives_count
            selected_locomotive_number = 1
    print('locomotive config updated')

def configsetup():
    global default_game_name, port, clients_number, frequency, game_profile_type, selected_locomotive, selected_locomotive_number, default_game_number
    global thrust_button_up, thrust_button_down, brake_button_up, brake_button_down, brake_locomotive_button_up, brake_locomotive_button_down, reverse_button_up, reverse_button_down, sand_button_up, sand_button_down
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, locomotives_count, ButConfig, game_profiles_counter, but_timeout_timer
    if os.path.exists(os.path.join(BASE_DIR, 'config.ini')):
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        default_game_number = int(config['HOST']['default_game_number'])
        default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
        game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
        port = int(config['NETWORK']['Port'])
        clients_number = int(config['NETWORK']['clients_number'])
        frequency = int(config['EV3']['Frequency'])

        if os.path.exists('game_profiles'):
            if game_profile_type == 0 and os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini')):
                config.read(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini'))
                game_profiles_counter = int(config['GAME_PROFILES']['game_profiles_counter'])
                locomotives_count = int(config['LOCOMOTIVES']['locomotives_count'])
                selected_locomotive = config['LOCOMOTIVES']['1']
                selected_locomotive_number = 1
                thrust_button_up = config[selected_locomotive]['thrust_button_up']
                thrust_button_down = config[selected_locomotive]['thrust_button_down']
                brake_button_up = config[selected_locomotive]['brake_button_up']
                brake_button_down = config[selected_locomotive]['brake_button_down']
                brake_locomotive_button_up = config[selected_locomotive]['brake_locomotive_button_up']
                brake_locomotive_button_down = config[selected_locomotive]['brake_locomotive_button_down']
                reverse_button_up = config[selected_locomotive]['reverse_button_up']
                reverse_button_down = config[selected_locomotive]['reverse_button_down']
                sand_button_up = config[selected_locomotive]['sand_button_up']
                sand_button_down = config[selected_locomotive]['sand_button_down']
                thrust_pos = int(config[selected_locomotive]['thrust_position_number'])
                brake_pos = int(config[selected_locomotive]['brake_position_number'])
                brakeloc_pos = int(config[selected_locomotive]['brake_locomotive_position_number'])
                sand_pos = int(config[selected_locomotive]['sand_position_number'])
            elif game_profile_type == 1 and os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.py')):
                ButConfig = importlib.import_module(f'game_profiles.{default_game_name}')
                but_timeout_timer = ButConfig.but_timeout_timer
                locomotives_count = ButConfig.locomotives_count
                selected_locomotive_number = 1
            else:
                configcreate()
        else:
            configcreate()
    else:
        configcreate()

def configcreate():
    global default_game_name, clients_number, port, frequency, game_profiles_counter, game_profile_type, default_game_number, locomotives_count, selected_locomotive, selected_locomotive_number
    if not os.path.exists(os.path.join(BASE_DIR, 'config.ini')):
        print('No config file, creating new')
        default_game_number = int(input('Enter default game number (default 1): '))
        clients_number = int(input('Enter number of clients: '))
        port = int(input('Enter port: '))
        frequency = int(input('Enter frequency: '))
        game_profiles_counter = int(input('Enter number of game_profiles: '))
        config['HOST'] = {
            'default_game_number': str(default_game_number),
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
            config.set('GAME_PROFILES', f'game_name.{i}', input(f'Enter game name {i}: '))
            config.set('GAME_PROFILES', f'game_profile_type.{i}', input(f'Enter game profile type {i}: '))
        try:
            configfile = open(os.path.join(BASE_DIR, 'config.ini'), 'w')
            config.write(configfile)
        except Exception as e:
            print('Cannot create config file:', e)
    else:
        default_game_number = int(config['HOST']['default_game_number'])
        clients_number = int(config['NETWORK']['clients_number'])
        port = int(config['NETWORK']['port'])
        frequency = int(config['EV3']['frequency'])
        game_profiles_counter = int(config['GAME_PROFILES']['game_profiles_counter'])
    if not os.path.exists(os.path.join(BASE_DIR, 'game_profiles')):
        try:
            os.mkdir(os.path.join(BASE_DIR, f'game_profiles'))
            print('created "game_profiles" folder in script folder')
        except Exception as e:
            print('Cannot create folder:', e)
            exit()
    config.read(os.path.join(BASE_DIR, 'config.ini'))
    default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
    game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
    for i in range(1, game_profiles_counter + 1):
        config.read(os.path.join(BASE_DIR, 'config.ini'))
        current_game_name = config['GAME_PROFILES'][f'game_name.{i}']
        if config['GAME_PROFILES'][f'game_profile_type.{i}'] == '0':
            if os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.ini')):
                print('game profile already exist:', current_game_name)
            else:
                config.clear()
                print(f'Creating new game profile: {current_game_name}.ini')
                locomotives_count = int(input('enter number of locomotives: '))
                config['LOCOMOTIVES'] = {
                    'locomotives_count': str(locomotives_count)
                }
                for i in range(1, locomotives_count + 1):
                    config.set('LOCOMOTIVES', str(i), input(f'Enter locomotive name {i}: '))
                selected_locomotive = config['LOCOMOTIVES']['1']
                selected_locomotive_number = 1
                for i in range(1, locomotives_count + 1):
                    config[config['LOCOMOTIVES'][str(i)]] ={
                        'thrust_position_number': input('Enter thrust position number: '),
                        'brake_position_number': input('Enter brake position number: '),
                        'brake_locomotive_position_number': input('Enter brake locomotive position number: '),
                        'sand_position_number': input('Enter sand position number: '),
                        'thrust_button_up': input('Enter thrust button up: '),
                        'thrust_button_down': input('Enter thrust button down: '),
                        'brake_button_up': input('Enter brake button up: '),
                        'brake_button_down': input('Enter brake button down: '),
                        'brake_locomotive_button_up': input('Enter brake locomotive button up: '),
                        'brake_locomotive_button_down': input('Enter brake locomotive button down: '),
                        'reverse_button_up': input('Enter reverse button up: '),
                        'reverse_button_down': input('Enter reverse button down: '),
                        'sand_button_up': input('Enter sand button up: '),
                        'sand_button_down': input('Enter sand button down: ')
                    }
                try:
                    configfile = open(os.path.join(BASE_DIR, f'game_profiles/{current_game_name}.ini'), 'w')
                    config.write(configfile)
                    print(f'Config {current_game_name}.ini created')
                except Exception as e:
                    print('Cannot create config file:', e)
        elif config['GAME_PROFILES'][f'game_profile_type.{i}'] == '1':
            if os.path.exists(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.py')):
                print('.py config already exists')
            else:
                print(f'Creating new game profile: {current_game_name}.py')
                try:
                    configfile = open(os.path.join(BASE_DIR, f'game_profiles/{default_game_name}.py'), 'w')
                    configfile.write('''from pynput.keyboard import Key, Controller

selected_locomotive = 'Locomotive 1'
locomotives_count = 1
but_timeout_timer = 5

keyboard = Controller()

def butpress(reverse_raw=0, thrust_raw=0, brake_raw=0, brake_locomotive_raw=0, sand_raw=0, but_timeout_raw=0, selected_locomotive_number=1):
    global reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data, but_timeout_flag, selected_locomotive, thrust_pos, brake_pos''')
                    print('Example .py config file created, remember to write your logic in it')
                    exit()
                except Exception as e:
                    print('Cannot create .py config file:', e)

def butpress():
    global sand_counter, but_timeout_flag, reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data

    if reverse_raw != reverse_data:
        if reverse_raw > reverse_data:
            for i in range(reverse_data, reverse_raw):
                keyboard.press(reverse_button_up)
                keyboard.release(reverse_button_up)
                time.sleep(but_press_delay)
        else:
            for i in range(reverse_raw, reverse_data):
                keyboard.press(reverse_button_down)
                keyboard.release(reverse_button_down)
                time.sleep(but_press_delay)
        reverse_data = reverse_raw

    if but_timeout_flag == 0:
        thrdelta = round((thrust_pos / 100) * thrust_raw)
        if thrust_data != thrdelta:
            if thrdelta > thrust_data:
                thrust_data += 1
                keyboard.press(thrust_button_up)
                keyboard.release(thrust_button_up)
            else:
                thrust_data -= 1
                keyboard.press(thrust_button_down)
                keyboard.release(thrust_button_down)
            but_timeout_flag = 1

        brkdelta = round((brake_pos / 100) * brake_raw)
        if brake_data != brkdelta:
            if brkdelta > brake_data:
                brake_data += 1
                keyboard.press(brake_button_up)
                keyboard.release(brake_button_up)
            else:
                brake_data -= 1
                keyboard.press(brake_button_down)
                keyboard.release(brake_button_down)
            but_timeout_flag = 1

        brklocdelta = round((brakeloc_pos / 100) * brake_locomotive_raw)
        if brake_locomotive_data != brklocdelta:
            if brklocdelta > brake_locomotive_data:
                brake_locomotive_data += 1
                keyboard.press(brake_locomotive_button_up)
                keyboard.release(brake_locomotive_button_up)
            else:
                brake_locomotive_data -= 1
                keyboard.press(brake_locomotive_button_down)
                keyboard.release(brake_locomotive_button_down)
            but_timeout_flag = 1

    if sand_raw != sand_data:
        sand_data = sand_raw
        if sand_data == 0:
            sand_counter = sand_counter + 1
            if sand_counter > sand_pos:
                sand_counter = 0
                for i in range(sand_pos): #That's bad I know
                    keyboard.press(sand_button_down)
                    keyboard.release(sand_button_down)
                    time.sleep(but_press_delay)
            else:
                keyboard.press(sand_button_up)
                keyboard.release(sand_button_up)

def selecting():
    global button_right_data, button_left_data, button_up_data, default_game_number, selected_locomotive_number, game_profile_selecting_flag
    if button_right_raw != button_right_data:
        button_right_data = button_right_raw
        if button_right_data == 0:
            if game_profile_selecting_flag:
                if default_game_number == game_profiles_counter:
                    default_game_number = 1
                else:
                    default_game_number += 1
                selected_locomotive_number = 1
            else:
                if selected_locomotive_number == locomotives_count:
                    selected_locomotive_number = 1
                else:
                    selected_locomotive_number += 1
            configupdate()

    if button_left_raw != button_left_data:
        button_left_data = button_left_raw
        if button_left_data == 0:
            if game_profile_selecting_flag:
                if default_game_number == 1:
                    default_game_number = game_profiles_counter
                else:
                    default_game_number -= 1
                selected_locomotive_number = 1
            else:
                if selected_locomotive_number == 1:
                    selected_locomotive_number = locomotives_count
                else:
                    selected_locomotive_number -= 1
            configupdate()

    if button_up_raw != button_up_data:
        button_up_data = button_up_raw
        if button_up_data == 0:
            if game_profile_selecting_flag == 0:
                game_profile_selecting_flag = 1
            else:
                game_profile_selecting_flag = 0

configsetup()

sock.bind(("", port))
sock.listen(clients_number)
print("Server starts")
con, addr = sock.accept()
print("connection: ", con)
print("client address: ", addr)

con.sendall(json.dumps({'freq': frequency,'type': 0,'usedisp': usedisp,'usehost': setup_1,'usebut': setup_2}).encode('utf-8'))

while ready_flag != 'ready':
    ready_flag = con.recv(32).decode('utf-8')
    print(ready_flag)


# if type == 1:
#     maximum_values = json.loads(con.recv(1024).decode('utf-8'))
#     print("maxvalues: ", maximum_values)
#     while True:

while True:
    try:
        if not con.recv(1024):
            print('Client disconnected')
            con.close()
            exit()
    except (BrokenPipeError, ConnectionResetError):
        print('Client emergency disconnected')
        con.close()
        exit()
    if but_timeout_flag == 1:
        counter += 1
        if counter >= but_timeout_timer:
            counter = 0
            but_timeout_flag = 0
    if game_profile_selecting_flag == 0:
        sentphoto()
    else:
        sentphoto(default_game_name)
    getinfo()
    if game_profile_type == 1:
        ButConfig.butpress(reverse_raw, thrust_raw, brake_raw, brake_locomotive_raw, sand_raw, but_timeout_flag, selected_locomotive_number)
        but_timeout_flag = ButConfig.but_timeout_flag
        selected_locomotive = ButConfig.selected_locomotive
        selecting()
    else:
        butpress()
        selecting()
    # print(reverse_raw, thrust_raw, brake_raw, brake_locomotive_raw, sand_raw)
    time.sleep(0.01)

