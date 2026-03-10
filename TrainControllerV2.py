import socket
from ev3dev2.display import Display # noqa
from ev3dev2.sensor import INPUT_2  # noqa
from ev3dev2.motor import LargeMotor, OUTPUT_D, OUTPUT_B, OUTPUT_C, MediumMotor  # noqa
from ev3dev2.sensor.lego import ColorSensor, TouchSensor  # noqa
from ev3dev2.button import Button  # noqa
import time
from PIL import Image  # noqa
import threading
import select
import json

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

freq = 0
type = 0
usedisp = 0
usehost = 0
usebut = 0
config = {'freq': 0, 'type': 0, 'usedisp': 0, 'usehost': 0, 'usebut': 0}
image = 'None'
imagenew = 'DE2'
counter = 5 # how many times sensors will be checked if it gives None
data = {rev: 0, thr: 0, brk: 0, brkloc: 0, sand: 0}

sock = socket.socket()
display = Display()
but = Button()
revsen = ColorSensor()
thrmot = MediumMotor(OUTPUT_B)
brklocmot = LargeMotor(OUTPUT_C)
brkmot = LargeMotor(OUTPUT_D)
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
    except Exception as e:
        print("Connection broken, error: {}, press enter to reconnect or backspace to exit".format(e))
        # sock.close()
        while but.enter == False:
            if but.backspace == True:
                exit()
            time.sleep(0.01)
        connect()

def meetup():        # !Call after calib()!
    global freq, type, usedisp, usehost, usebut, config, maxvalues
    connect()
    config = sock.recv(1024)
    config = config.decode('utf-8')
    print(config)
    config = json.loads(config)
    print(config)
    freq = config['freq']
    usedisp = config['usedisp']
    usehost = config['usehost']
    usebut = config['usebut']
    type = config['type']
    if config['type'] == 1:
        sock.send(json.dumps(maxvalues).encode('utf-8'))
    sock.send(bytes('ready', encoding='utf-8'))

def calib():
    global thrmax, brkmax, brklocmax, type, maxvalues
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
    maxvalues = {'thrmax': thrmax, 'brkmax': brkmax, 'brklocmax': brklocmax}
    print("Calibration done")
    print(thrmax, brkmax, brklocmax)

def getdata(a):
    global thrmax, brkmax, brklocmax, rev, type, counter
    c = 0
    b = None
    if a == 'thr':
        while b == None:
            b = thrmot.position
            c = c + 1
            if c == counter:
                return 101
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
        while b == None:
            b = brkmot.position
            c = c + 1
            if c == counter:
                return 102
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
        while b == None:
            b = brklocmot.position
            c = c + 1
            if c == counter:
                return 103
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
        while b == None:
            b = revsen.color
            c = c + 1
            if c == counter:
                return 104
        if b == 3:
            return 2
        elif b == 1:
            return 1
        elif b == 5:
            return 0
        else:
            return 4
    elif a == 'all':
        if type == 1:
            while b == None:
                b = thrmot.position
                c = c + 1
                if c == counter:
                    b = 101
                    c = 0
            thr = b
            b = None
            while b == None:
                b = brkmot.position
                c = c + 1
                if c == counter:
                    b = 102
                    c = 0
            brk = b
            b = None
            while b == None:
                b = brklocmot.position
                c = c + 1
                if c == counter:
                    b = 103
                    c = 0
            brkloc = b
            b = None
            while b == None:
                b = revsen.color
                c = c + 1
                if c == counter:
                    b = 104
                    c = 0
            return {'thr': thr,'brk': brk,'brkloc': brkloc,'rev': b, 'sand': snd.is_pressed}
        else:
            while b == None:
                b = thrmot.position
                c = c + 1
                if c == counter:
                    b = 101
                    c = 0
            thr = round((b / thrmax) * 100)
            b = None
            while b == None:
                b = brkmot.position
                c = c + 1
                if c == counter:
                    b = 102
                    c = 0
            brk = round((b / brkmax) * 100)
            b = None
            while b == None:
                b = brklocmot.position
                c = c + 1
                if c == counter:
                    b = 103
                    c = 0
            brkloc = round((b / brklocmax) * 100)
            b = None
            while b == None:
                b = revsen.color
                c = c + 1
                if c == counter:
                    b = 104
                    c = 0
            if b == 3:
                b = 2
            elif b == 1:
                b = 1
            elif b == 5:
                b = 0
            else:
                b = 4
            return {'thr': thr,'brk': brk,'brkloc': brkloc,'rev': b, 'sand': snd.is_pressed}
    print('getdata: Wrong argument')
    return None

def screenupdate():
    global image, imagenew, start
    while True:
        ready, _, _ = select.select([sock], [], [], 0)
        if ready:
            imagenew = sock.recv(256).decode('utf-8')
            if image != imagenew:
                print("Image changed from", image, 'to', imagenew)
                image = imagenew
                if image != 'None':
                    try:
                        imagedisplay = Image.open("/home/robot/myproject/{}.bmp".format(image))
                        display.clear()
                        display.update()
                        display.image.paste(imagedisplay, (0, 0))
                        display.update()
                        start = time.perf_counter()
                    except FileNotFoundError:
                        print("image not found: {}".format(image))
                    except Exception as e:
                        print("Error occurred: {}".format(e))
        elif (time.perf_counter() - start) >= 0.5:
            display.update()
            start = time.perf_counter()
        time.sleep(0.001)


start = time.perf_counter()

calib()
meetup()

if usedisp == 1:
    screen_thread = threading.Thread(target=screenupdate, daemon=True)
    screen_thread.start()

while but.backspace == False:
    data = json.dumps({'thr': getdata('thr'), 'brk': getdata('brk'), 'brkloc': getdata('brkloc'), 'rev': getdata('rev'), 'sand': snd.is_pressed}) + '\n'
    try:
        sock.sendall(data.encode('utf-8'))
    except Exception as e:
        print("Error occurred: {}".format(e))
        connect()
    time.sleep(round(1 / freq, 4))