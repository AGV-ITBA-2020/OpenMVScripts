# Untitled - By: Javier - Sun Aug 2 2020

import sensor, image, time
import time
from pyb import UART


sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 500)

clock = time.clock()

uart = UART(1, 38400,timeout=10000)
time.sleep(500)

uart.writechar(55) #Comunica que la inicialización es correcta
uart.writechar(55) #Comunica que la inicialización es correcta
time.sleep(500)

#uart.writechar(55) #Comunica que la inicialización es correcta
b=uart.readchar()
print(b)
while(True):
    clock.tick()
    img = sensor.snapshot()
    #print(clock.fps())
