# Untitled - By: Javier - Sat Aug 8 2020

import sensor, image, time, pyb

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)

green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
tag_families = 0 | image.TAG36H11 # Familia de tags a identificar
clock = time.clock()
Th=60
while(True):
    pyb.delay(50);
    clock.tick()
    green_led.off()
    img = sensor.snapshot()
    #img.histeq(adaptive=False);

    #img.median(2, percentile=0.25) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.

    #img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    #img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    #img.median(1, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    #img.find_blobs()
    #3img.median(1, percentile=1)


    #img.dilate(2) #Dilato por si el camino se cortó
    for tag in img.find_apriltags(families=tag_families): # defaults to TAG36H11 without "families".
        green_led.on()
        print("Veo\n");
        #img.draw_rectangle(tag.rect(), color = 127)
        #img.draw_cross(tag.cx(), tag.cy(), color = 127)
    img.binary([(Th,255)],invert=True)#Binarizo la imagen: 255 si pertenece a la línea 0 si no.

    #print(clock.fps())
