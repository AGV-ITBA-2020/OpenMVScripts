# Untitled - By: Javier - Sat Jul 25 2020
# based on https://openmv.io/blogs/news/linear-regression-line-following

import sensor, image, time

GRAYSCALE_THRESHOLD = (80, 255)

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQQVGA)
sensor.skip_frames(time = 5000) # let auto-gain/auto-white-balance run before using images

def track_line():
    img = sensor.snapshot() #Acá ecualizaban pero creo que eso no nos sirve a nosotros

    #th = img.get_histogram().get_threshold() # Threshold automático para separar clases (No anda muy bien)
    #thf= (th[0],255)

    img.binary([GRAYSCALE_THRESHOLD]) #Pongo el threshold a manopla
    img.negate()                      #Como la línea va a ser negra, se la niega
    img.erode(1)                      #Erode para eliminar ruido, achicar la línea -> menos puntos para la regresión

    line = img.get_regression([(255, 255)], robust=True) #Obtiene la línea por regresión lineal sobre los píxeles blancos
    if line:
        img.draw_line(line.line(), color=127, thickness=2)

while(1):
    track_line()
