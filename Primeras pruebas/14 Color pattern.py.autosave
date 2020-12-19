# Untitled - By: Javier - Fri Dec 18 2020

import sensor, image, time
import ulab as np

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()

def simpleColorPattern(greenThImg): ##Este método binariza y toma solo cuando hay patrón de ambas imágenes
    blueThImg=greenThImg.copy()
    n_pix=2; #número de pixeles para tomar en cuenta de cada color
    green_threshold = (0, 100, -128, -32, -128, 127) ##TH de día
    blue_threshold = (0,100,   -128,127,   -128,-30) # L A B #TH de noche
    blueThImg.binary([blue_threshold])
    greenThImg.binary([green_threshold])
    blue_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    green_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for h in range(sensor.height()): #Obtengo la primer fila binarizada
        for w in range(sensor.width()): #Obtengo la primer fila binarizada
            blue_row[w]=blueThImg.get_pixel(w,h)[0]#Obtengo la primer fila
            green_row[w]=greenThImg.get_pixel(w,h)[0]#Obtengo la primer fila
        for w in range(sensor.width()):
            if(w>=n_pix and w <sensor.width()-n_pix):
                count=0;
                for n in range(n_pix):
                    if(green_row[w-n-1]):
                        count+=1;
                    if(blue_row[w+n+1]):
                        count+=1;
                if(count >= n_pix+1):
                    greenThImg.set_pixel(w,h,[255, 255, 255])
                else:
                    greenThImg.set_pixel(w,h,[0, 0, 0])
            else:
                greenThImg.set_pixel(w,h,[0, 0, 0])

while(True):
    clock.tick()
    img = sensor.snapshot().histeq()
    simpleColorPattern(img)
    #green_threshold = (11, 94, -88, -28, -52, 125) # L A B
    #img.binary([green_threshold])
    print(clock.fps())
