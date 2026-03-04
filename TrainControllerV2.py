import socket
from ev3dev2.display import Display # noqa
from ev3dev2.sensor import INPUT_2  # noqa
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, OUTPUT_C, MediumMotor  # noqa
from ev3dev2.sensor.lego import ColorSensor, TouchSensor  # noqa
from ev3dev2.button import Button  # noqa
import time
from PIL import Image  # noqa

ip = "192.168.1.185"
port = 9600

thr = 0
thrmin = 0
thrmax = 0
brk = 0
brkmin = 0
brkmax = 0
brkloc = 0
brklocmin = 0
brklocmax = 0
rev = 0
sand = 0
#train = 0
#data = 0b0

config = 0
freq = 0
type = 0
usedisp = 0
usehost = 0
usebut = 0
image = 'None'
imagenew = 'DE2'

sock = socket.socket()
display = Display()
but = Button()
revsen = ColorSensor()
thrmot = MediumMotor(OUTPUT_B) #-4 -- 85
brklocmot = LargeMotor(OUTPUT_C) #4 -- 70
brkmot = LargeMotor(OUTPUT_D) #4 -- -70
snd = TouchSensor(INPUT_2)
revsen.MODE_COL_COLOR # noqa

def connect():
    global ip, port
    if ip == "0":
        ip = input("Enter IP: ")
        if port == 0:
            port = input("Enter port: ")
    try:
        print("Trying to connect")
        sock.connect((ip, port))
        print("Connected")
        return 1
    except BrokenPipeError or ConnectionResetError:
        print("Connection broken, press enter to reconnect or backspace to exit")
        while but.enter == False:
            if but.backspace == True:
                exit()
            time.sleep(0.01)
        connect()

def meetup():
    global freq, type, usedisp, usehost, usebut, config
    connect()
    # sock.send(freq.to_bytes()) #приветствие
    # sock.listen(1)
    config = sock.recv(3)
    config = int.from_bytes(config, "big")
    print(config)
    usebut = config & 1
    usehost = (config >> 1) & 1
    usedisp = (config >> 2) & 1
    type = (config >> 3) & 1
    freq = config >> 4
    print(freq, type, usedisp, usehost, usebut)

def calib():
    global thrmax, brkmax, brklocmax, type
    print("Calibration, move all sliders down and press enter")
    while but.enter == False:
        time.sleep(0.001)
    thrmot.position = 0
    brkmot.position = 0
    brklocmot.position = 0
    while but.enter == True:
        time.sleep(0.001)
    print("Now move all sliders up and press enter again")
    while but.enter == False:
        time.sleep(0.001)
    thrmax = thrmot.position
    brkmax = brkmot.position
    brklocmax = brklocmot.position
    while but.enter == True:
        time.sleep(0.001)
    print("Calibration done")
    print(thrmax, brkmax, brklocmax)

def getdata(a):
    global thrmax, brkmax, brklocmax, rev, type
    b = 0
    if a == 'thr':
        while b == 0 or b == None:
            b = thrmot.position
        if type == 0:
            if b == 0:
                return 0
            b = round((b / thrmax) * 100)
            if b > 100:
                return 100
            if b < 0:
                return 0
            else:
                return b
        else:
            return b
    elif a == 'brk':
        while b == 0 or b == None:
            b = brkmot.position
        if type == 0:
            if b == 0:
                return 0
            b = round(b / brkmax * 100)
            if b > 100:
                return 100
            if b < 0:
                return 0
            else:
                return b
        else:
            return b
    elif a == 'brkloc':
        while b == 0 or b == None:
            b = brklocmot.position
        if type == 0:
            if b == 0:
                return 0
            b = round(b / brklocmax * 100)
            if b > 100:
                return 100
            if b < 0:
                return 0
            else:
                return b
        else:
            return b
    elif a == 'but':
        b = but.enter
        b = b << 1
        b = (b & but.up) << 1
        b = (b & but.right) << 1
        b = (b & but.down) << 1
        b = (b & but.left) << 1
        b = b & but.backspace
        print(b)
        return b
    elif a == 'rev':
        while b == 0 or b == None:
            b = revsen.color
        if b == 3:
            return 0
        elif b == 1:
            return 1
        elif b == 5:
            return 2
        else:
            return 1
    return None

def screenupdate():
    global image, imagenew
    imagenew = sock.recv(256).decode('utf-8')
    if image != imagenew:
        print("Image changed", image, imagenew)
        image = imagenew
        if image != 'None':
            try:
                imagedisplay = Image.open("/home/robot/myproject/{}.bmp".format(image))
                display.clear()
                display.update()
                display.image.paste(imagedisplay, (0, 0))
                display.update()
            except FileNotFoundError:
                print("image not found: {}".format(image))
            except Exception as e:
                print("Error occurred: {}".format(e))

calib()
meetup()
# while True:
#     data = getdata('rev') << 7
#     data = (data | getdata('thr')) << 7
#     data = (data | getdata('brk')) << 7
#     data = (data | getdata('brkloc')) << 1
#     data = data | snd.is_pressed
#     print('Before converting:', data)
#     data = data.to_bytes(3, byteorder="big")
#     print('After converting:', data)
#     sock.send(data)
#     print('tic')
#     time.sleep(0.01)

while True:
    # if usedisp == 1:


    if type == 0:
        data = getdata('rev') << 7
        data = (data | getdata('thr')) << 7
        data = (data | getdata('brk')) << 7
        data = (data | getdata('brkloc')) << 1
        data = data | snd.is_pressed
        data = data.to_bytes(3, byteorder="big")
        sock.send(data)
    time.sleep(round(1 / freq, 4))