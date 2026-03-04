import socket
import time

sock = socket.socket()
port = 9600

image = 'DE2'
freq = 0
type = 0
usedisp = 0
usehost = 0
usebut = 0
config = 0

data = 0
reverse = 0
thrust = 0
brake = 0
brakeloc = 0
sand = 0
but = 0

freq = int(input("Частота в диапазоне 0-127"))
if freq < 0 or freq > 127:
    freq = int(input("Неверно указана частота, впишите значение в диапазоне 0-127"))
type = int(input("Тип передачи 0/1"))
if type < 0 or type > 1:
    type = int(input("Неверно указан тип передачи, укажите значение в диапазоне 0-1"))
usedisp = int(input("Использовать дисплей 0/1"))
if usedisp < 0 or usedisp > 1:
    usedisp = int(input("Неверно указано использование дисплея, укажите значение в диапазоне 0-1"))
usehost = int(input("Передавать данные на хост 0/1"))
if usehost < 0 or usehost > 1:
    usehost = int(input("Неверно указано приём данных от хоста, укажите значение в диапазоне 0-1"))
usebut = int(input("Использовать кнопки 0/1"))
if usebut < 0 or usebut > 1:
    usebut = int(input("Неверно указано использование кнопок, укажите значение в диапазоне 0-1"))

print(freq, type, usedisp, usehost, usebut)

config = freq << 1
config = (config | type) << 1
config = (config | usedisp) << 1
config = (config | usehost) << 1
config = config | usebut

# config = config.to_bytes((config.bit_length() + 7) // 8, 'big')
config = config.to_bytes(2, byteorder="big")
print(config)
print(int.from_bytes(config, "big"))

sock.bind(("", port))
sock.listen(1)
print("Server starts")
con, addr = sock.accept()     # принимаем клиента
print("connection: ", con)
print("client address: ", addr)

# print(con.recv(1))
con.send(config)
while True:
    if usedisp == 1:
        if len(image) < 256:
            con.send(bytes(f'{image}', encoding="utf-8"))
        else:
            print('Нельзя инициализировать фото - недопустимая длина символов')
            con.send(bytes('None', encoding="utf-8"))
    data = con.recv(4)
    data = int.from_bytes(data, byteorder="big")
    print(bin(data))
    sand = data & 1
    brakeloc = (data >> 1) & 127
    brake = (data >> 8) & 127
    thrust = (data >> 15) & 127
    reverse = (data >> 22) & 3
    print(reverse, thrust, brake, brakeloc, sand)
    time.sleep(0.03)