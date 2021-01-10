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
    n_pix=3; #número de pixeles para tomar en cuenta de cada color
    green_threshold = (0, 100, -128, -30, -128, 127) ##TH de día
    blue_threshold = (0,100,   -128,127,   -128,-40) # L A B #TH de noche
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
    greenThImg.dilate(2)
def fast_line_detect(greenThImg): ##Este método binariza y toma solo cuando hay patrón de ambas imágenes
    row_2_analyze=sensor.height()-10
    blueThImg=greenThImg.copy()#(sensor.width()/2,row_2_analyze,sensor.width(),sensor.height())
    n_pix=1 #numero de pixeles para tomar en cuenta de cada color
    dist_entre_colores=1# Esta es la diferencia de pixeles para evitar la zona enel medio que se juntan los colores
    green_threshold = (0, 100, -128, -30, -128, 127) ##TH de día
    blue_threshold = (0,100,   -128,127,   -128,-35) # L A B #TH de noche
    blueThImg.binary([blue_threshold])
    blueThImg.dilate(2)
    greenThImg.binary([green_threshold])
    greenThImg.dilate(2)
    blue_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    green_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    output_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for w in range(sensor.width()):
        blue_row[w]=blueThImg.get_pixel(w,row_2_analyze)[0]
        green_row[w]=greenThImg.get_pixel(w,row_2_analyze)[0]
    for w in range(sensor.width()):
        if(w>=n_pix+dist_entre_colores and w <sensor.width()-n_pix-dist_entre_colores):
            count=0;
            for n in range(n_pix):
                if(green_row[w-n-1-dist_entre_colores]):
                    count+=1;
                if(blue_row[w+n+1+dist_entre_colores]):
                    count+=1;
            if(count >= n_pix+1):
                output_row[w]= 255
            else:
                output_row[w]= 0
        else:
            output_row[w]= 0
    n_to_paint=6;
    greenThImg.clear()
    for w in range(sensor.width()):
        if output_row[w]==255:
            for i in range(n_to_paint):
                greenThImg.set_pixel(w,i-int(n_to_paint/2)+row_2_analyze,[255, 255, 255])
    return output_row

while(True):
    clock.tick()
    img = sensor.snapshot().histeq()
    img.lens_corr(1.8)
    fast_line_detect(img)

    print(clock.fps())
