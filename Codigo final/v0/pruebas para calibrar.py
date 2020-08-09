# Untitled - By: Javier - Sat Aug 8 2020

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)

clock = time.clock()
Th=60
while(True):
    clock.tick()
    img = sensor.snapshot().binary([(180,255)], invert=False, zero=True)

    #img.median(2, percentile=0.25) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.

    img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    #img.median(1, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    #img.find_blobs()
    #3img.median(1, percentile=1)

    #img.binary([(Th,255)],invert=True)#Binarizo la imagen: 255 si pertenece a la línea 0 si no.
    #img.dilate(2) #Dilato por si el camino se cortó
    print(clock.fps())
