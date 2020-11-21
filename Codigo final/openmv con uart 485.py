''' Librerías '''
import sensor, image, time, pyb, utime
from pyb import UART
import ulab as np
from ulab import numerical
import machine

'''########################  Variables universales ###########################'''
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)
center_pixel = sensor.width() / 2

red_led=pyb.LED(1);
red_led.on()
uart = UART(1, 115200) ##UART que se utiliza con el baudrate dado y un timeout (este último realmente no hace falta
msg_buf=np.zeros(sensor.width(), dtype=np.int8) #Buffer en el que se guardan los msjs enviados por el openMV
state_to_n = {"Line follower":0,"Fork left":1,"Fork right":2,"Merge":3,"Error":4, "Idle":5 } #Estados del openMV y su mapeo a números, útil para las comunicaciones
n_to_state= {0:"Line follower",1:"Fork left",2:"Fork right",3:"Merge",4:"Error", 5:"Idle", 10:"Send data" }
tag_families = 0 | image.TAG36H11 # Familia de tags a identificar
 # Led usado para checkar funcionamiento en tiempo real
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
dirPin = pyb.Pin("P2", pyb.Pin.OUT_PP)
clock = time.clock()
dirPin.low();
prevD=0;

green_led.on()
'''########################  Parámetros calibrables ###########################'''
Th=160 ##Threshold
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
def compute_simple_error(first_row,prevD):
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
        prevD=d;
    else:
        err=1;
        print("No se detectó línea")

    return d,lines_found,err;

#Encuentra un april tag en la cámara (Si hay más de uno es un error)
def find_tags():
    #tags = 0;
    #tags = img.find_apriltags(families=tag_families) #Busco tags
    tag_nmbr=0;
    tag_found=False;
    #if tags:
        #tag_found=True;
        #tag_nmbr=tags[0].id()
        #green_led.on() #Prendo led si hay tag a la vista
    #else:
        #green_led.off()
    return tag_found,tag_nmbr;

#Filtra la imagen y devuelve la primer fila binarizada.
def img_filter_and_get_first_row(img):
    green_threshold = (11, 94, -88, -28, -52, 125) # L A B
    img.binary([green_threshold])
    img.erode(1)
    img.dilate(2)
    first_row = np.zeros(sensor.width(), dtype=np.uint8) #Aloco memoria para procesar
    for i in range(sensor.width()): #Obtengo la primer fila binarizada
        first_row[i]=img.get_pixel(i,sensor.height()-10)[0] #Obtengo la primer fila
#first_row[i]=img.get_pixel(i,sensor.height()-1) #Obtengo la primer fila
    return first_row

def sendPrevMsg():
    dirPin.high()
    uart.writechar(msg_buf[0]) ##Envía el mensaje previo a la CIAA
    uart.writechar(msg_buf[1])
    uart.writechar(0)
    uart.writechar(0) #Mando 4 bytes de info ya que la ciaa se interrumpe con 4*n bytes obtenidos
    #print("D sent",msg_buf[0], "SecBuf Sent =",msg_buf[1])
    dirPin.low() #Ojo con esto, podría ir luego de un poco del procesamiento así no es bloqueante la uart

'''########################  Inicialización ###########################'''


####Configs marcos
#sensor.set_auto_gain(False,gain_db=0)
#sensor.set_auto_whitebal(False)
##sensor.set_gainceiling(128)
#sensor.set_saturation(-3)
#sensor.set_contrast(3)


state="Line follower" #Se empieza en idle
fml = fork_merge_logic()
fml.new_openMV_state(state) #Para la lógica de paso de uniones se comunica el estado del openMV

Accumulate_error=True;

'''########################  Loop principal ###########################'''
start = utime.ticks_ms()
while(True):
    green_led.toggle()
    red_led.off()
    if (uart.any()):
        clock.tick()
        red_led.on()
        ciaaMsg=n_to_state[int(uart.readchar())] #Se le comunica el nuevo estado
        sendPrevMsg()
        if(ciaaMsg != "Send data" ): #Si no es un send data, es un nuevo estado que le pone al openmv
            state=ciaaMsg
            fml.new_openMV_state(state)
        #print("CIAA SAID: New state ->",state)
        fork_or_merge_passed=0;
        img = sensor.snapshot().histeq() #Obtengo la imagen
        tag_found,tag_nmbr = find_tags() #Se busca si hay algún tag
        first_row = img_filter_and_get_first_row(img) #Obtengo la primer fila fitlrada y binarizada.
        d,lines_found,err = compute_simple_error(first_row,prevD) #Aplico el algoritmo para obtener el error y cantidad de lineas encontradas
        #d=-d
        if lines_found==0:
            d=msg_buf[0];
            if Accumulate_error:
                if d<0 and d > -122:
                    d=d-5
                if d>0 and d < 121:
                    d=d+5


        fml.feed(lines_found)
        #print("lines_found %d, fml state: %s" % (lines_found, fml.state))
        if fml.state=="Union passed":
            fml.clear_state()
            fork_or_merge_passed=1;
        gen_next_msg(msg_buf,d,err,tag_found,tag_nmbr,fork_or_merge_passed)
        print_args = (d,tag_found,tag_nmbr,fork_or_merge_passed, err,clock.fps(),prevD)
        print("D: %d, tag: %r,tag n:%d, fomp: %r, err: %r, fps: %f, %f" % print_args)
