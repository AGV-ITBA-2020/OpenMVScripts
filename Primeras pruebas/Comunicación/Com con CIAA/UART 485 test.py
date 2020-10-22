''' Librerías '''
import sensor, image, time, pyb, utime
from pyb import UART
import ulab as np
from ulab import numerical

'''########################  Variables universales ###########################'''
uart = UART(1, 115200,timeout=1000) ##UART que se utiliza con el baudrate dado y un timeout (este último realmente no hace falta
state_to_n = {"Line follower":0,"Fork left":1,"Fork right":2,"Merge":3,"Error":4, "Idle":5 } #Estados del openMV y su mapeo a números, útil para las comunicaciones
n_to_state= {0:"Line follower",1:"Fork left",2:"Fork right",3:"Merge",4:"Error", 5:"Idle"}

red_led=pyb.LED(1); # Led usado para checkar funcionamiento en tiempo real
green_led=pyb.LED(2); # Led usado para mostrar que se ve el tag
dirPin = pyb.Pin("P2", pyb.Pin.OUT_PP)

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

state="Idle" #Se empieza en idle
freq_sample=10 #Frecuencia de sampling


'''########################  Loop principal ###########################'''
def sendMsg():
    dirPin.high()
    uart.writechar(25) ##Envía el mensaje previo a la CIAA
    uart.writechar(31)
    uart.writechar(0)
    uart.writechar(0) #Mando 4 bytes de info ya que la ciaa se interrumpe con 4*n bytes obtenidos
    dirPin.low() #Ojo con esto, podría ir luego de un poco del procesamiento así no es bloqueante la uart

while(True):
    if (uart.any()):
        state=n_to_state[int(uart.readchar())] #Se le comunica el nuevo estado
        print("CIAA SAID: New state ->",state)
        sendMsg()
        #print("D sent",msg_buf[0], "SecBuf Sent =",msg_buf[1])
        img = sensor.snapshot() #Obtengo la imagen
        #Procesa la imagen para preparar el siguiente mensaje
