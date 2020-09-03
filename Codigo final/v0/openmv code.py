''' Librerías '''
import sensor, image, time, pyb, utime
from pyb import UART
import ulab as np
from ulab import numerical

'''########################  Variables universales ###########################'''
uart = UART(1, 38400,timeout=10000) ##UART que se utiliza con el baudrate dado y un timeout (este último realmente no hace falta
msg_buf=np.zeros(sensor.width(), dtype=np.int8) #Buffer en el que se guardan los msjs enviados por el openMV
state_to_n = {"Line follower":0,"Fork left":1,"Fork right":2,"Merge":3,"Error":4, "Idle":5 } #Estados del openMV y su mapeo a números, útil para las comunicaciones
n_to_state= {0:"Line follower",1:"Fork left",2:"Fork right",3:"Merge",4:"Error", 5:"Idle"}
tag_families = 0 | image.TAG36H11 # Familia de tags a identificar
red_led=pyb.LED(1); # Led usado para checkar funcionamiento en tiempo real
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
clock = time.clock()

'''########################  Parámetros calibrables ###########################'''
Th=60 ##Threshold
hist_len=6 #Cantidad de muestras a promediar para saber si se pasó una unión

'''########################  Parámetros calibrables ###########################'''
class fork_merge_logic: ##Clase para manejar la lógica si pasó por un camino o no
    def __init__(self):
        self.hist_len=hist_len
        self.n_lines_hist= [0]*self.hist_len;
        self.state="Idle"
    def new_openMV_state(self, newState):#Cada vez que se cambia el estado del openMV se tiene que llamar a esta función
        if newState == "Fork left" or newState == "Fork right" or newState == "Merge": #Si hay una unión en el siguiente paso
            self.state="Before union"
    def clear_state(self):
        self.state="Idle"
    def feed(self,n_lines):
        #print(self.n_lines_hist)
        self.n_lines_hist.pop(0)
        self.n_lines_hist.append(n_lines)
        if self.state=="Before union" and all(x >= 2 for x in self.n_lines_hist): #Si vio 2 líneas en las últimas mediciones identifica que está en la union
            self.state = "During union"
        elif self.state=="During union" and all(x == 1 for x in self.n_lines_hist): ##Si estaba en la unión y ahora solo ve 1 líne significa que ya la pasó
            self.state = "Union passed"

'''########################  Funciones ###########################'''
#Con los datos a transmitir genera el buffer a enviar a uart
def gen_next_msg(msg_buf,d,err,tag_found,tag_nmbr,fork_or_merge_passed):
    msg_buf[0]=d;
    sec=err*128+fork_or_merge_passed*64 + tag_found*32 + tag_nmbr; #No funciona con shifts wtf
    msg_buf[1]=sec; #tag_nmbr<32 para que no se interponga con los otros bits

#Devuelve el centro de línea que se encuentre más cercano al pixel del centro
def get_closer_line_center(line_centers,center_pixel):
    lc=np.array(line_centers)
    dif= lc - center_pixel
    arg=numerical.argmin(abs(dif))
    return line_centers[arg]

#Dada la primer fila de pixeles y el estado del openmv, calcula el error y cantidad de líneas
def compute_simple_error(first_row):
    prev=0 # Asumo que fuera de la imagen no hay líneas
    d=0;
    err=0
    lines_found=0;
    line_borders=[]

    ##Busco los bordes de las líneas encontradas. Siempre van a a ser una cantidad par!
    for i in range(len(first_row)): #Busco los extremos de la imagen viendo cuando cambia de color
        if(prev==0 and first_row[i]==255) or (prev==255 and first_row[i]==0) or ((i==len(first_row)-1 and first_row[i]==255)) : #Si en el pixel anterior no había línea y en el siguiente si, hay borde. También el caso inverso
            line_borders.append(i)
        prev=first_row[i]
    if (first_row[len(first_row)-1]==255 and  first_row[len(first_row)-2]==0) : #Para el caso de un punto blanco en la esquina, se ignora.
        line_borders.pop()

    if line_borders: #Si hay líneas
        line_centers=[]
        for i in range(int(len(line_borders)/2)): #Calculo los centros de las líneas a partir de los bordes
            line_centers.append((line_borders[i*2]+line_borders[i*2])/2)
        lines_found = len(line_centers)
        ##Aquí se podría agregar un código para encontrar errores: + de 2 líneas, 2 lineas en modo normal, etc.
        if state=="Line follower":
            d = center_pixel - get_closer_line_center(line_centers,center_pixel) ##Porlas si hay error
        elif state=="Fork left":
            d = center_pixel - line_centers[0] ##Línea de la izquierda
        elif state == "Fork right":
            d = center_pixel - line_centers[-1] ##Línea de la derecha
        elif state == "Merge":
            d = center_pixel - get_closer_line_center(line_centers,center_pixel) ##En el merge tomo la línea con menor error, total convergen a la misma.
    else:
        err=1;
        print("No se detectó línea")

    return d,lines_found,err;

#Encuentra un april tag en la cámara (Si hay más de uno es un error)
def find_tags():
    tags = img.find_apriltags(families=tag_families) #Busco tags
    tag_nmbr=0;
    tag_found=False;
    if tags:
        tag_found=True;
        tag_nmbr=tags[0].id()
        green_led.on() #Prendo led si hay tag a la vista
    else:
        green_led.off()
    return tag_found,tag_nmbr;

#Filtra la imagen y devuelve la primer fila binarizada.
def img_filter_and_get_first_row(img):
    img.binary([(180,255)], invert=False, zero=True) ##Elimino reflexiones en las cintas

    img.median(2, percentile=1) #Filtros de mediana para eliminar ruido y los apriltags de las mediciones.
    img.median(2, percentile=1) #Reemplazan cada pixel por el pixel "más blanco" de su alrededor.

    img.binary([(Th,255)],invert=True)#Binarizo la imagen: 255 si pertenece a la línea 0 si no.
    img.dilate(2) #Dilato por si el camino se cortó

    first_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for i in range(sensor.width()): #Obtengo la primer fila binarizada
        first_row[i]=img.get_pixel(i,sensor.height()-1) #Obtengo la primer fila
    return first_row


'''########################  Inicialización ###########################'''
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
center_pixel = sensor.width() / 2

time.sleep(500)
uart.writechar(55) #Manda un byte al arduino para iniciar la comunicación.
b=uart.readchar()
state=n_to_state[int(b)] #Se espera el estado inicial.
freq_sample=2 #Frecuencia de sampling
fml = fork_merge_logic()
fml.new_openMV_state(state) #Para la lógica de paso de uniones se comunica el estado del openMV


'''########################  Loop principal ###########################'''
start = utime.ticks_ms()

while(True):
    if (uart.any()):
        state=n_to_state[int(uart.readchar())] #Se le comunica el nuevo estado
        fml.new_openMV_state(state)
        print("ARDUINO SAID: New state ->",state)
    t_elapsed = utime.ticks_diff(utime.ticks_ms(), start)
    if (state != "Idle") and (t_elapsed/1000 > (1/freq_sample)): #Con una frecuencia determinada toma proceso de captura
        fork_or_merge_passed=0;
        clock.tick()
        start = utime.ticks_ms()
        uart.writechar(msg_buf[0]) ##Envía el mensaje previo a la CIAA
        uart.writechar(msg_buf[1])
        #print("D sent",msg_buf[0], "SecBuf Sent =",msg_buf[1])
        img = sensor.snapshot() #Obtengo la imagen
        tag_found,tag_nmbr = find_tags() #Se busca si hay algún tag
        first_row = img_filter_and_get_first_row(img) #Obtengo la primer fila fitlrada y binarizada.
        d,lines_found,err = compute_simple_error(first_row) #Aplico el algoritmo para obtener el error y cantidad de lineas encontradas
        fml.feed(lines_found)
        print("lines_found %d, fml state: %s" % (lines_found, fml.state))
        if fml.state=="Union passed":
            fml.clear_state()
            fork_or_merge_passed=1;
        gen_next_msg(msg_buf,d,err,tag_found,tag_nmbr,fork_or_merge_passed)
        print_args = (clock.fps(),d,tag_found,tag_nmbr,fork_or_merge_passed, err)
        #print("FPS: %d, D: %d, tag: %r,tag n:%d, fomp: %r, err: %r" % print_args)
