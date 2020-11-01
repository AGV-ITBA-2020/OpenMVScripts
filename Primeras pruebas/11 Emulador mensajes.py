''' Librerías '''
import sensor, image, time, pyb, utime
from pyb import UART
import ulab as np
from ulab import numerical

'''########################  Variables universales ###########################'''
uart = UART(1, 115200) ##UART que se utiliza con el baudrate dado y un timeout (este último realmente no hace falta
state_to_n = {"Line follower":0,"Fork left":1,"Fork right":2,"Merge":3,"Error":4, "Idle":5 } #Estados del openMV y su mapeo a números, útil para las comunicaciones
n_to_state= {0:"Line follower",1:"Fork left",2:"Fork right",3:"Merge",4:"Error", 5:"Idle"}

red_led=pyb.LED(1); # Led usado para checkar funcionamiento en tiempo real
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
dirPin = pyb.Pin("P2", pyb.Pin.OUT_PP)
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag

dirPin.low()

'''########################  Parámetros calibrables ###########################'''
Th=60 ##Threshold
hist_len=6 #Cantidad de muestras a promediar para saber si se pasó una unión

'''########################  Parámetros calibrables ###########################'''

'''########################  Funciones ###########################'''

#Filtra la imagen y devuelve la primer fila binarizada.


'''########################  Inicialización ###########################'''
sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 2000)
center_pixel = sensor.width() / 2

msg_buf=np.zeros(sensor.width(), dtype=np.int8) #Buffer en el que se guardan los msjs enviados por el openMV
i=0;
'''########################  Loop principal ###########################'''
def parse_command(msgIn):
    d=0;fork_or_merge_passed=0;tag_found=0;tag_nmbr=0; err=0;
    if(msgIn[0]=='D'):
        d = int(msgIn[2:])
    elif((msgIn[0]=='F') or (msgIn[0]=='M')):
        fork_or_merge_passed=1;
    elif(msgIn[0]=='T'):
        tag_found=1;
        tag_nmbr=int(msgIn[2:])
    else:
        print("Wrong Format")
    msg_buf[0]=d;
    sec=err*128+fork_or_merge_passed*64 + tag_found*32 + tag_nmbr; #No funciona con shifts wtf
    msg_buf[1]=sec; #tag_nmbr<32 para que no se interponga con los otros bits

def sendMsg():
    dirPin.high()
    uart.writechar(msg_buf[0]) ##Envía el mensaje previo a la CIAA
    uart.writechar(msg_buf[1])
    uart.writechar(0)
    uart.writechar(0) #Mando 4 bytes de info ya que la ciaa se interrumpe con 4*n bytes obtenidos
    dirPin.low() #Ojo con esto, podría ir luego de un poco del procesamiento así no es bloqueante la uart

while(True):
    msgIn = input();
    while(uart.any()):
        i=uart.readchar() ## Limpio buffer
    print(msgIn)
    if(len(msgIn)>=1):
        parse_command(msgIn);
        print("MB0: ", msg_buf[0]," MB1: ",msg_buf[1])
        #while(not uart.any()): ##Cuando llega de la CIAA, le mando el msj que corresponde
            #i=i+1
        #i=uart.readchar()
        #sendMsg()
