# Filtra con filtros de mediana para evitar tomar los puntos negros de los apriltags
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

##Lógica de fork y merge
class fork_merge_logic:
    def __init__(self):
        self.hist_len=10
        self.n_lines_hist= [0]*self.hist_len;
        self.state="Idle"
    def notify_union_ahead(self): #Cuando el próximo paso de la misión es un fork/merge se tiene que llamar a esta función
        self.state="Before Union"
    def clear_state(self):
        self.state="Idle"
    def feed(self,n_lines):
        #print(self.n_lines_hist)
        self.n_lines_hist.pop(0)
        self.n_lines_hist.append(n_lines)
        if self.state=="Before Union" and all(x >= 2 for x in self.n_lines_hist): #Si vio 2 líneas en las últimas mediciones identifica que está en la union
            self.state = "During Union"
        elif self.state=="During Union" and all(x == 1 for x in self.n_lines_hist): ##Si estaba en la unión y ahora solo ve 1 líne significa que ya la pasó
            self.state = "Union Passed"

##Procesamiento de camino
def get_closer_line_center(line_centers,center_pixel):
    lc=np.array(line_centers)
    dif= lc - center_pixel
    arg=numerical.argmin(abs(dif))
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


state = "ForkL"
fml = fork_merge_logic()
fml.notify_union_ahead()

while(True):
    tags_found=0;
    clock.tick()
    img = sensor.snapshot() #Obtengo la memoria

    img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    img.median(1, percentile=1) #Reemplazan cada pixel por el pixel más "blanco de su alrededor.
    img.median(1, percentile=1)

    img.binary([(TH,255)],invert=True)#Binarizo la imagen: 255 si pertenece a la línea 0 si no.
    img.dilate(2) #Dilato por si el camino se cortó

    first_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for i in range(sensor.width()): #Obtengo la primer fila binarizada
        first_row[i]=img.get_pixel(i,sensor.height()-1) #Obtengo la primer fila

    d,lines_found = compute_simple_error(first_row,state) #Aplico el algoritmo para obtener el error y cantidad de lineas encontradas
    fml.feed(lines_found)



    print_args = (clock.fps(),d,lines_found,fml.state)
    print("FPS: %d, ErrorMeas: %d (pixels), Lines found: %d , fml state= %s" % print_args)
