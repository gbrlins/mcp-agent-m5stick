from m5stack import *
from m5ui import *
from uiflow import *
import unit
import time

setScreenColor(0x068538)

env2_0 = unit.get(unit.ENV2, unit.PORTA)

import network
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect('Gabirol', '24082024')

lcd.clear()
lcd.print('Conectando...', 0, 0, 0xFFFF00)

for i in range(20):
    if wifi.isconnected():
        break
    wait_ms(500)

if wifi.isconnected():
    ip = wifi.ifconfig()[0]
    lcd.clear()
    lcd.print('IP: ' + ip, 0, 60, 0x00FF00)
    lcd.print('Porta: 5000', 0, 90, 0x00FF00)
else:
    lcd.clear()
    lcd.print('WiFi Error', 0, 0, 0xFF0000)

import socket
import json

def serve():
    s = socket.socket()
    s.bind(('0.0.0.0', 5000))
    s.listen(1)
    lcd.print('Esperando...', 0, 130, 0xFFFF00)

    while True:
        c, a = s.accept()
        r = c.recv(1024).decode()

        temp = env2_0.temperature
        hum = env2_0.humidity
        pres = env2_0.pressure

        data = {'temp': round(temp, 2), 'hum': round(hum, 2), 'pres': round(pres, 2)}
        body = json.dumps(data)

        resp = 'HTTP/1.1 200 OK\r\n'
        resp = resp + 'Content-Type: application/json\r\n'
        resp = resp + 'Content-Length: ' + str(len(body)) + '\r\n'
        resp = resp + '\r\n'
        resp = resp + body

        c.sendall(resp.encode())
        c.close()

serve()
