import json
import socket
import time
import select
import configparser
import pyautogui as keyboard # noqa
import os
import importlib

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
game_profile_selecting_flag = 0

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

reverse_data = 0 #All ..._data and ..._raw variables provided as a percentage (0-100%)
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

def sentphoto(a = ''):
    global image
    if usedisp == 1:
        if image != selected_locomotive:
            image = selected_locomotive
            con.send(bytes(f'{image}', encoding="utf-8"))
            print('Sent photo:', image)
            if a != '':
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
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, selected_locomotive, ButConfig, game_profile_type
    if game_profile_selecting_flag == 0:
        if game_profile_type == 0:
            if os.path.exists(f'game profiles/{default_game_name}'):
                config.read(f'game profiles/{default_game_name}.ini')
            else:
                print('config not found with name', default_game_name)
                exit('TODO')
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
        config.read('config.ini')
        default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
        game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
        if game_profile_type == 0:
            if os.path.exists(f'game profiles/{default_game_name}'):
                config.read(f'game profiles/{default_game_name}.ini')
            else:
                print('config not found with name', default_game_name)
                exit('TODO')
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
            ButConfig = importlib.import_module(f'game profiles.{default_game_name}')
    print('locomotive config updated')

def configsetup():
    global default_game_name, port, clients_number, frequency, type, usedisp, game_profile_type, selected_locomotive, selected_locomotive_number, default_game_number
    global thrust_button_up, thrust_button_down, brake_button_up, brake_button_down, brake_locomotive_button_up, brake_locomotive_button_down, reverse_button_up, reverse_button_down, sand_button_up, sand_button_down
    global thrust_pos, brake_pos, brakeloc_pos, sand_pos, locomotives_count, ButConfig
    if os.path.exists('config.ini'):
        config.read('config.ini')
        default_game_number = int(config['HOST']['default_game_number'])
        default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
        game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
        port = int(config['NETWORK']['Port'])
        clients_number = int(config['NETWORK']['clients_number'])
        frequency = int(config['EV3']['Frequency'])

        if os.path.exists('game profiles'):
            if game_profile_type == 0 and os.path.exists(f'game profiles/{default_game_name}.ini'):
                config.read(f'game profiles/{default_game_name}.ini')
                locomotives_count = config['LOCOMOTIVES']['locomotives_count']
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
            elif game_profile_type == 1 and os.path.exists(f'game profiles/{default_game_name}.py'):
                ButConfig = importlib.import_module(f'game profiles.{default_game_name}')
            else:
                print('config not found with name', default_game_name)
                exit('TODO')
        else:
            print('directory "game profiles" not found')
            try:
                os.mkdir('game profiles')
                print('create one in script folder, remember to add your .ini/.py file')
            except Exception as e:
                print('Cannot create folder:',e)
            exit('TODO')
    else:
        configcreate()

def configcreate():
    global default_game_name, clients_number, port, frequency, game_profiles_counter, game_profile_type, default_game_number
    print('No config file, creating new')
    default_game_number = int(input('Enter default game number (default 1): '))
    clients_number = int(input('Enter number of clients: '))
    port = int(input('Enter port: '))
    frequency = int(input('Enter frequency: '))
    game_profiles_counter = int(input('Enter number of game profiles: '))
    if not os.path.exists('game profiles'):
        try:
            os.mkdir('game profiles')
            print('created "game profiles" folder in script folder')
        except Exception as e:
            print('Cannot create folder:', e)
            exit()
    else:
        print('"game profiles" folder already exists')
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
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print('Config created, remember to config game profile before starting program')
    except Exception as e:
        print('Cannot create config file:', e)
    config.read('config.ini')
    default_game_name = config['GAME_PROFILES'][f'game_name.{default_game_number}']
    game_profile_type = int(config['GAME_PROFILES'][f'game_profile_type.{default_game_number}'])
    exit('TODO')

def butpress():
    global sand_counter, but_timeout, reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data

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
    if game_profile_selecting_flag == 0:
        sentphoto()
    else:
        sentphoto(default_game_name)
    getinfo()
    if game_profile_type == 1:
        ButConfig.butpress()
    else:
        butpress()
        selecting()
    # print(reverse_raw, thrust_raw, brake_raw, brake_locomotive_raw, sand_raw)
    time.sleep(0.01)

