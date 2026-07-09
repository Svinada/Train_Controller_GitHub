# EV3Locomotive
![Photo of train controller](/Pictures/Photo1.jpg)

# Video
![video on youtube]()

# Features
* Operate locomotive by emulation of keystrokes on PC
* Works via Wi-Fi
* Support custom keystroke logic via .py module
* Show your own .bmp photos or text on display

# Installation
## On ev3
### 1. ev3dev
Install ev3dev on your ev3 by following [this instruction](https://www.ev3dev.org/docs/getting-started/)
### 2. Connect
Connect to your ev3 via SSH by following [this instruction](https://www.ev3dev.org/docs/tutorials/connecting-to-ev3dev-with-ssh/)
### 3. Cloning repo
Clone repo by this command:
```
git clone https://github.com/Svinada/Ev3Locomotive.git
```
### 4. Run script
First of all run `PCdriver.exe` or `PC.py` on your PC. On ev3 open created folder by 
```
cd Ev3Locomotive
```
and run `TrainControllerV2.py` by 
```
python3 TrainControllerV2.py
```
Script will requre calibration, just follow its instruction. Don't forget that all your sliders (motors) are at the maximal value when calibration is done and `PCdriver.exe` will emulate keystrokes when ev3 will connect. When calibration done, script will requre local IP of your PC and port which you entered in `PCdriver.exe` (it contains in `config.ini`). By the way script does not remember entered IP and port and will ask it everytime, but you can open script by 
```
nano TrainControllerV2.py
```
and change line (14 and 15) with your ip and port:
```
...
import select
import json

ip = "" <-- Change this, ip should be string
port = 0 <-- And this, port should be number

thrust = 0
thrust_maximum = 0
...
```
Then press `CTRL+X`, save modified buffer by `Y` and press `Enter`.
### 5. Selecting different locomotives or game profiles
`Left` and `right` buttons on ev3 will change current locomotive, but if at first you press `up` button, you are able to change game profiles (press button `up` again to load current profile and select locomotives).
### 6. Exit
Stop script by pressing `backspace` button on ev3 or press `CTRL+C` in SSH window.
## On PC
### With default configs
Just download latest release with name `PCdriver_and_default_configs.zip` [from here](https://github.com/Svinada/Ev3Locomotive/releases) (default port is `9600`, you can change it in `config.ini`).
### Without default configs
Download `PCdriver.exe` (it will create `config.ini` and folder `game_profiles` in the folder where it was launched) [from here](https://github.com/Svinada/Ev3Locomotive/releases).

# Creating config
When script can't find `config.ini`, folder `game_profiles` or game profile in that folder, it will create necessary file.
Example `config.ini` looks like:
```
[HOST]
default_game_number = 1 <-- Number of config which will load at startup

[NETWORK]
port = 9600 <-- port which will use by client (ev3) for connecting and data exchange
clients_number = 1 <-- beta variable, it's better not to change

[EV3]
frequency = 30 <-- sensor refresh rate

[GAME_PROFILES]
game_profiles_counter = 2 <-- number of game profiles
game_name.1 = Derail Valley
game_profile_type.1 = 0
game_name.2 = Metrostroi
game_profile_type.2 = 1
```
## Game profiles have two types:
## type 0
Config contains:
* Number of locomotives
* Locomotive names

And every locomotive contains:
* keybinds for throttle, brake, locomotive brake, reverse, sand
* Number of position for throttle, brake, locomotive brake, reverse, sand

Example `Derail Valley.ini` with one locomotive (DE2) looks like:
```
[LOCOMOTIVES]
locomotives_count = 1
1 = DE2

[DE2]
but_timeout_timer = 2 <-- delay between keystrokes, abstract value, I couldn't calculate the ratio to seconds :)
thrust_position_number = 11
brake_locomotive_position_number = 7
brake_position_number = 11
sand_position_number = 1
thrust_button_up = t
thrust_button_down = g
brake_button_up = u
brake_button_down = j
brake_locomotive_button_up = i
brake_locomotive_button_down = k
reverse_button_up = y
reverse_button_down = h
sand_button_up = b
sand_button_down = n
```
Keystrokes processed by login in `PC.py` (function `butpress()`), fits for games with simple keystroke handling like Derail Valley
## type 1
Custom logic of keystrokes via `.py` file. You can use standard timeout timer from PC.py by raising the flag `but_timeout_flag = 1`.Keystrokes works via `pynput.keyboard` and allow you to create any logic of keystrokes. Importing module should have:
```
selected_locomotive = 'Locomotive name'
locomotives_count = 1
but_timeout_timer = 2
but_timeout_flag = 0

def butpress(reverse_raw=0, thrust_raw=0, brake_raw=0, brake_locomotive_raw=0, sand_raw=0, but_timeout_raw=0, selected_locomotive_number=1):
    # your code here...
```
Example `Metrostroi.py` looks like:
```
from pynput.keyboard import Key, Controller
import time

selected_locomotive = '81-717'
locomotives_count = 2
reverse_data = 0
brake_data = 0
brake_locomotive_data = 0
sand_data = 0
thrust_data = 0
but_timeout_flag = 0
but_timeout_timer = 2

keyboard = Controller()

def metrostroi_press(key, duration=0.25):
    keyboard.press(key)
    time.sleep(duration)  # Metrostroi требует минимум ~0.1-0.2 секунды
    keyboard.release(key)

def butpress(reverse_raw=0, thrust_raw=0, brake_raw=0, brake_locomotive_raw=0, sand_raw=0, but_timeout_raw=0, selected_locomotive_number=1):
    global reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data, but_timeout_flag, selected_locomotive, thrust_pos, brake_pos
    if selected_locomotive_number == 1:
        selected_locomotive = '81-717'
        thrust_pos = 6
        brake_pos = 6
    elif selected_locomotive_number == 2:
        selected_locomotive = '81-760'
        thrust_pos = 7
        brake_pos = 6
    if reverse_raw != reverse_data:
        if reverse_raw > reverse_data:
            for i in range(reverse_data, reverse_raw):
                metrostroi_press('0')
        else:
            for i in range(reverse_raw, reverse_data):
                metrostroi_press('9')
        reverse_data = reverse_raw
    if but_timeout_raw == 0:
        thrdelta = round((thrust_pos / 100) * thrust_raw)
        if thrust_data != thrdelta:
            if thrdelta > thrust_data:
                if thrdelta > 2 and thrust_data == 2:
                    thrust_data += 1
                    keyboard.press(Key.shift_l)
                    time.sleep(0.25)
                    metrostroi_press('w')
                    keyboard.release(Key.shift_l)
                else:
                    thrust_data += 1
                    metrostroi_press('w')
            else:
                thrust_data -= 1
                metrostroi_press('s')
            but_timeout_flag = 1

        brkdelta = round((brake_pos / 100) * brake_raw)
        if brake_data != brkdelta:
            if brkdelta > brake_data:
                brake_data += 1
                metrostroi_press('r')
            else:
                brake_data -= 1
                metrostroi_press('f')
            but_timeout_flag = 1

    if sand_raw == 1:
        keyboard.press(Key.space)
    else:
        keyboard.release(Key.space)
```