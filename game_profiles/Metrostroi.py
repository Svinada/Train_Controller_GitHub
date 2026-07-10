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
    time.sleep(duration)
    keyboard.release(key)

def butpress(reverse_raw=0, thrust_raw=0, brake_raw=0, brake_locomotive_raw=0, sand_raw=0, but_timeout_raw=0, selected_locomotive_number=1):
    global reverse_data, brake_data, brake_locomotive_data, sand_data, thrust_data, but_timeout_flag, selected_locomotive, thrust_pos, brake_pos
    if selected_locomotive_number == 1:
        # changing locomotive properties
        selected_locomotive = '81-717'
        thrust_pos = 6
        brake_pos = 6
    elif selected_locomotive_number == 2:
        # changing locomotive properties here too
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