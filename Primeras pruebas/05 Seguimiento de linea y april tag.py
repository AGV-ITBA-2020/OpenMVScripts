# Untitled - By: Javier - Thu Jul 30 2020
import ulab as np
import sensor, image, time, pyb
from ulab import numerical

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)

clock = time.clock()
framesize=sensor.get_framesize()
center_pixel = sensor.width() / 2
TH=50

red_led=pyb.LED(1); # Uso los leds para ver si el programa corre en tiempo real
green_led=pyb.LED(2);
blue_led=pyb.LED(3);

tag_families = 0 | image.TAG36H11 # (default family)


def get_closer_line_center(line_centers,center_pixel):
    lc=np.array(line_centers)
    dif= lc - center_pixel
    arg=numerical.argmin(abs(dif))
    #line_centers[numerical.argmin(abs(center_pixel*np.ones(len(line_centers)) - np.array(line_centers)))]

    return line_centers[arg]

def compute_simple_error(first_row,case):
    prev=0 # Asumo que fuera de la imagen no hay cienta
    d=0;
    lines_found=0;
    line_borders=[]
    for i in range(len(first_row)): #Busco los extremos de la imagen viendo cuando cambia de color
        if(prev==0 and first_row[i]==255) or (prev==255 and first_row[i]==0):
            line_borders.append(i)
        prev=first_row[i]
    if (first_row[len(first_row)-1]==255 and  first_row[len(first_row)-1]==0) : #Para el caso de un punto blanco en la esquina, se ignora.
        line_borders.pop()

    if line_borders: #Si hay líneas
        line_centers=[]
        for i in range(int(len(line_borders)/2)): #Calculo sus centros
            line_centers.append((line_borders[i*2]+line_borders[i*2])/2)
        lines_found = len(line_centers)
        if case=="Normal":
            d = center_pixel - get_closer_line_center(line_centers,center_pixel)
        elif case=="ForkL":
            d = center_pixel - line_centers[0]
        elif case == "ForkR":
            d = center_pixel - line_centers[-1]
        elif case == "Merge":
            d = center_pixel - get_closer_line_center(line_centers,center_pixel)
    else:
        print("No se detectó línea")

    return d,lines_found;


while(True):
    clock.tick()
    img = sensor.snapshot() #Obtengo la memoria

    first_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for i in range(sensor.width()): #Obtengo la primer fila binarizada
        first_row[i]=img.get_pixel(i,sensor.height()-1) #Obtengo la primer fila y aplico el threshold (Se podría hacer con la función binary
        if first_row[i] > TH:
            first_row[i] = 0
        else:
            first_row[i] = 255

    d,lines_found = compute_simple_error(first_row,"ForkL") #Aplico el algoritmo para obtener el error y cantidad de lineas encontradas

    tags = img.find_apriltags(families=tag_families) #Busco tags
    tags_found=0;
    if tags:
        tags_found=1;
        green_led.on() #Prendo led si hay tag a la vista
        for tag in tags: # defaults to TAG36H11 without "families".
            img.draw_rectangle(tag.rect(), color = 127)
            img.draw_cross(tag.cx(), tag.cy(), color = 127)
            #print_args = (family_name(tag), tag.id(), (180 * tag.rotation()) / math.pi)
            #print("Tag Family %s, Tag ID %d, rotation %f (degrees)" % print_args)
    else:
        green_led.off()
    img.binary([(TH,255)],invert=True)#Muestro lo que ve en binario la cámara
    print_args = (clock.fps(), tags_found, d,lines_found)
    print("FPS: %d, Tag Found: %d, ErrorMeas: %d (pixels), Lines found: %d " % print_args)
    #print(clock.fps())
