# Untitled - By: Javier - Thu Jul 30 2020
import ulab as np
import sensor, image, time
from ulab import numerical

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)

clock = time.clock()
framesize=sensor.get_framesize()
center_pixel = sensor.width() / 2
TH=80

red_led=LED(1); # Uso los leds para ver si el programa corre en tiempo real
green_led=LED(2);
blue_led=LED(3);

tag_families = 0 | image.TAG36H11 # (default family)


def compute_simple_error(first_row,case):
    prev=0 # Asumo que fuera de la imagen no hay cienta
    d=0;
    line_borders=[]
    for i in range(len(first_row)):
        if(prev==0 and first_row[i]==255) or (prev==255 and first_row[i]==0):
            line_borders.append(i)

    if line_borders:
        if (first_row[len(first_row)-1]==255 and  first_row[len(first_row)-1]==0) : #Para el caso de un punto negro en la esquina, se ignora.
            line_borders.pop()
        line_centers=[]
        for i in range(int(len(line_borders)/2)):
            line_centers.append((line_borders[i*2]+line_borders[i*2])/2)

        if case=="Normal":
            d = center_pixel - line_centers[numerical.argmin(abs(center_pixel - line_centers))]
        elif case=="ForkL":
            d = center_pixel - line_centers[0]
        elif case == "ForkR":
            d = center_pixel - line_centers[-1]
        elif case == "Merge":
            d = center_pixel - line_centers[numerical.argmin(abs(center_pixel - line_centers))]
    else:
        print("No se detectó línea")

    return d;


while(True):
    clock.tick()
    img = sensor.snapshot()

    first_row = np.array([0]*sensor.width(), dtype=np.uint8)) #Aloco memoria para procesar
    for i in range(sensor.width()): #Obtengo la primer fila binarizada
        first_row[i]=img.get_pixel(i,sensor.height()-1) #Obtengo la primer fila
        if first_row[i] > TH:
            first_row[i] = 0
        else:
            first_row[i] = 255

    d = compute_simple_error(first_row,"Normal")

    tags = img.find_apriltags(families=tag_families)
    tags_found=0;
    if tags:
        tags_found=1;
        green_led.on()
        for tag in tags: # defaults to TAG36H11 without "families".
            img.draw_rectangle(tag.rect(), color = 127)
            img.draw_cross(tag.cx(), tag.cy(), color = 127)
            #print_args = (family_name(tag), tag.id(), (180 * tag.rotation()) / math.pi)
            #print("Tag Family %s, Tag ID %d, rotation %f (degrees)" % print_args)
    else:
        green_led.off()

    print_args = (clock.fps(), tags_found, d)
    print("FPS: %d, Tag Found: %d, ErrorMeas: %d (degrees)" % print_args)
    print(clock.fps())
