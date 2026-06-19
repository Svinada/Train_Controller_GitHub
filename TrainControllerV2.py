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

thrust = 0
thrust_maximum = 0
brake = 0
brake_maximum = 0
brake_locomotive = 0
brake_locomotive_maximum = 0
reverse = 0
sand = 0

frequency = 0
data_type = 0
use_display = 0
setup_1 = 0
setup_2 = 0
config = {'freq': 0, 'type': 0, 'usedisp': 0, 'usehost': 0, 'usebut': 0}
image = 'None'
image_new = 'DE2'
sensor_attempts = 5 # how many times sensors will be checked if it gives None

Socket = socket.socket()
Display = Display()
Button = Button()
ReverseSensor = ColorSensor()
ThrustSensor = MediumMotor(OUTPUT_B)
BrakeLocomotiveSensor = LargeMotor(OUTPUT_C)
BrakeSensor = LargeMotor(OUTPUT_D)
SandSensor = TouchSensor(INPUT_2)
ReverseSensor.MODE_COL_COLOR # noqa

def connect():
    global ip, port
    if ip == "":
        ip = input("Enter IP: ")
    if port == 0:
        port = input("Enter port: ")
    try:
        print("Trying to connect")
        Socket.connect((ip, port))
        print("Connected")
        return 1
    except Exception as e:
        print("Connection broken, error: {}".format(e)) # , press enter to reconnect or backspace to exit
        Socket.close()
        while not Button.enter:
            if Button.backspace:
                exit()
            time.sleep(0.01)
        connect()
        return None


def meetup():        # !Call after calib()!
    global frequency, data_type, use_display, setup_1, setup_2, config, maximum_values
    connect()
    config = Socket.recv(1024)
    config = config.decode('utf-8')
    print(config)
    config = json.loads(config)
    print(config)
    frequency = config['freq']
    use_display = config['usedisp']
    setup_1 = config['usehost']
    setup_2 = config['usebut']
    data_type = config['type']
    if config['type'] == 1:
        Socket.send(json.dumps(maximum_values).encode('utf-8'))
    Socket.send(bytes('ready', encoding='utf-8'))

def calib():
    global thrust_maximum, brake_maximum, brake_locomotive_maximum, data_type, maximum_values
    print("Calibration, move all sliders down and press enter")
    while not Button.enter:
        time.sleep(0.001)
    ThrustSensor.position = 0
    BrakeSensor.position = 0
    BrakeLocomotiveSensor.position = 0
    while Button.enter:
        time.sleep(0.001)
    print("Now move all sliders up and press enter again")
    while not Button.enter:
        time.sleep(0.001)
    thrust_maximum = ThrustSensor.position
    brake_maximum = BrakeSensor.position
    brake_locomotive_maximum = BrakeLocomotiveSensor.position
    while Button.enter:
        time.sleep(0.001)
    maximum_values = {'thrmax': thrust_maximum, 'brkmax': brake_maximum, 'brklocmax': brake_locomotive_maximum}
    print("Calibration done")
    print(thrust_maximum, brake_maximum, brake_locomotive_maximum)

def getdata(argument):
    global thrust_maximum, brake_maximum, brake_locomotive_maximum, reverse, data_type, sensor_attempts
    attempts_counter = 0
    sensor_data = None
    if argument == 'thr':
        while sensor_data is None:
            sensor_data = ThrustSensor.position
            attempts_counter = attempts_counter + 1
            if attempts_counter == sensor_attempts:
                return 101
        if data_type == 0:
            if sensor_data == 0:
                return 0
            sensor_data = round((sensor_data / thrust_maximum) * 100)
            if sensor_data > 100:
                return 100
            if sensor_data < 0:
                return 0
            else:
                return sensor_data
        else:
            return sensor_data
    elif argument == 'brk':
        while sensor_data is None:
            sensor_data = BrakeSensor.position
            attempts_counter = attempts_counter + 1
            if attempts_counter == sensor_attempts:
                return 102
        if data_type == 0:
            if sensor_data == 0:
                return 0
            sensor_data = round(sensor_data / brake_maximum * 100)
            if sensor_data > 100:
                return 100
            if sensor_data < 0:
                return 0
            else:
                return sensor_data
        else:
            return sensor_data
    elif argument == 'brkloc':
        while sensor_data is None:
            sensor_data = BrakeLocomotiveSensor.position
            attempts_counter = attempts_counter + 1
            if attempts_counter == sensor_attempts:
                return 103
        if data_type == 0:
            if sensor_data == 0:
                return 0
            sensor_data = round(sensor_data / brake_locomotive_maximum * 100)
            if sensor_data > 100:
                return 100
            if sensor_data < 0:
                return 0
            else:
                return sensor_data
        else:
            return sensor_data
    elif argument == 'but':
        sensor_data = Button.enter
        sensor_data = sensor_data << 1
        sensor_data = (sensor_data & Button.up) << 1
        sensor_data = (sensor_data & Button.right) << 1
        sensor_data = (sensor_data & Button.down) << 1
        sensor_data = (sensor_data & Button.left) << 1
        sensor_data = sensor_data & Button.backspace
        print(sensor_data)
        return sensor_data
    elif argument == 'rev':
        while sensor_data is None:
            sensor_data = ReverseSensor.color
            attempts_counter = attempts_counter + 1
            if attempts_counter == sensor_attempts:
                return 104
        if sensor_data == 3:
            return 2
        elif sensor_data == 1:
            return 1
        elif sensor_data == 5:
            return 0
        else:
            return 4
    # elif argument == 'all':
    #     if data_type == 1:
    #         while sensor_data is None:
    #             sensor_data = ThrustSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 101
    #                 attempts_counter = 0
    #         thrust = sensor_data
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = BrakeSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 102
    #                 attempts_counter = 0
    #         brake = sensor_data
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = BrakeLocomotiveSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 103
    #                 attempts_counter = 0
    #         brake_locomotive = sensor_data
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = ReverseSensor.color
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 104
    #                 attempts_counter = 0
    #         return {'thr': thrust,'brk': brake,'brkloc': brake_locomotive,'rev': sensor_data, 'sand': SandSensor.is_pressed}
    #     else:
    #         while sensor_data is None:
    #             sensor_data = ThrustSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 101
    #                 attempts_counter = 0
    #         thrust = round((sensor_data / thrust_maximum) * 100)
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = BrakeSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 102
    #                 attempts_counter = 0
    #         brake = round((sensor_data / brake_maximum) * 100)
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = BrakeLocomotiveSensor.position
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 103
    #                 attempts_counter = 0
    #         brake_locomotive = round((sensor_data / brake_locomotive_maximum) * 100)
    #         sensor_data = None
    #         while sensor_data is None:
    #             sensor_data = ReverseSensor.color
    #             attempts_counter = attempts_counter + 1
    #             if attempts_counter == sensor_attempts:
    #                 sensor_data = 104
    #                 attempts_counter = 0
    #         if sensor_data == 3:
    #             sensor_data = 2
    #         elif sensor_data == 1:
    #             sensor_data = 1
    #         elif sensor_data == 5:
    #             sensor_data = 0
    #         else:
    #             sensor_data = 4
    #         return {'thr': thrust,'brk': brake,'brkloc': brake_locomotive,'rev': sensor_data, 'sand': SandSensor.is_pressed}
    print('getdata: Wrong argument')
    return None

def screenupdate():
    global image, image_new, start
    while True:
        Display.update()
        if time.perf_counter() - start > 1:
            start = time.perf_counter()
            ready, _, _ = select.select([Socket], [], [], 0)
            Display.update()
            if ready:
                image_new = Socket.recv(256).decode('utf-8')
                if image != image_new:
                    print("Image changed from", image, 'to', image_new)
                    image = image_new
                    if image != 'None':
                        try:
                            imagedisplay = Image.open("/home/robot/TrainControllerV2/Pictures/{}.bmp".format(image))
                            Display.clear()
                            Display.update()
                            Display.image.paste(imagedisplay, (0, 0))
                            Display.update()
                        except FileNotFoundError:
                            print("image not found: {}".format(image))
                        except Exception as e:
                            print("Error occurred: {}".format(e))
        time.sleep(0.5)


start = time.perf_counter()

calib()
meetup()

if use_display:
    screen_thread = threading.Thread(target=screenupdate, daemon=True)
    screen_thread.start()

while not Button.backspace:
    data = json.dumps({'thr': getdata('thr'),
                       'brk': getdata('brk'),
                       'brkloc': getdata('brkloc'),
                       'rev': getdata('rev'),
                       'sand': SandSensor.is_pressed,
                       'butleft': Button.left,
                       'butup': Button.up,
                       'butright': Button.right,
                       'butdown': Button.down,
                       'butenter': Button.enter}) + '\n'
    try:
        Socket.sendall(data.encode('utf-8'))
    except Exception as e:
        print("Error occurred: {}".format(e))
        connect()
    time.sleep(round(1 / frequency, 4))
Socket.detach()
Socket.close()
exit() #