''' Librerías '''
import sensor, image, time, pyb, utime

sensor.reset()

sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)
#sensor.set_auto_gain(False,gain_db=0)
#sensor.set_auto_whitebal(False)
#sensor.set_gainceiling(128)
#sensor.set_saturation(-3)
#sensor.set_contrast(3)
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
tag_families = 0 | image.TAG36H11 # Familia de tags a identificar
clock = time.clock()
Th=170
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
    #img.median(1, percentile=1)


    #img.dilate(2) #Dilato por si el camino se cortó
    #for tag in img.find_apriltags(families=tag_families): # defaults to TAG36H11 without "families".
        #green_led.on()
        #print("Veo\n");
        #img.draw_rectangle(tag.rect(), color = 127)
        #img.draw_cross(tag.cx(), tag.cy(), color = 127)
    #img.binary([(Th,255)])#Binarizo la imagen: 255 si pertenece a la línea 0 si no.
    ##img.median(1, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    ##img.invert()
    #img.erode(2)
    #img.erode(2)
    #img.erode(2)
    #print(clock.fps())
