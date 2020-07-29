# Untitled - By: Javier - Mon Jul 27 2020

import sensor, image, time, utime
from pyb import LED


sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE) # or GRAYSCALE...
sensor.set_framesize(sensor.VGA) # or QQVGA...
sensor.set_windowing((640, 80))
sensor.skip_frames(time = 2000)
#clock = time.clock()

FPS=10
red_led=LED(1); # Uso los leds para ver si el programa corre en tiempo real
green_led=LED(2);
blue_led=LED(3);

while(True):
    #clock.tick()

    start = utime.ticks_ms()
    img = sensor.snapshot()
    #img = sensor.snapshot().cartoon(seed_threshold=0.1, floating_thresholds=0.05) #Pongo la función de cartoon para que consuma un poco de procesamiento

    t_elapsed = utime.ticks_diff(utime.ticks_ms(), start)
    if t_elapsed/1000 > (1/FPS): #Si la tarea tardó más de 1/FPS se pone en rojo
        green_led.off()
        red_led.on()
    else: #Sino en verde
        green_led.on()
        red_led.off()

    #print(clock.fps(), t_elapsed, 1/FPS )
#https://forums.openmv.io/viewtopic.php?t=689 Para correr el programa sin pasar info a la pc
