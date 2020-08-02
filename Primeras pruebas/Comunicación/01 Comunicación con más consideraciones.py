import sensor, image, time, pyb, utime
from pyb import UART
import ulab as np
from ulab import numerical

def emulate_outputs(count):
    if (count <100):
        d=50;
        err=0;
        tag_found=0;
        tag_nmbr=1;
        fork_or_merge_passed=0;
    elif(count <200):
        d=-50;
        err=0;
        tag_found=1;
        tag_nmbr=1;
        fork_or_merge_passed=0;
    elif(count <300):
        d=0;
        err=0;
        tag_found=0;
        tag_nmbr=1;
        fork_or_merge_passed=1;
    elif(count >= 300):
        d=0;
        err=0;
        tag_found=1;
        tag_nmbr=3;
        fork_or_merge_passed=0;

    return d,err,tag_found,tag_nmbr,fork_or_merge_passed;

def gen_next_msg(msg_buf,d,err,tag_found,tag_nmbr,fork_or_merge_passed):
    msg_buf[0]=d;
    msg_buf[1]=err<<7+fork_or_merge_passed<<6 + tag_found<<5 + tag_nmbr; #tag_nmbr<32 para que no se interponga con los otros bits

state_to_n = {"Line follower":0,"Fork Left":1,"Fork Right":2,"Merge":3,"Error":4 }
n_to_state= {0:"Line follower",1:"Fork Left",2:"Fork Right",3:"Merge",4:"Error"}

sensor.reset()
sensor.set_pixformat(sensor.GRAYSCALE)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 500)

# UART 3, and baudrate.
uart = UART(1, 38400,timeout=10000)
utime.sleep(500)

uart.write(b'\x48') #Comunica que la inicialización es correcta
b=uart.readchar()
print(b)
state=n_to_state[int(b[0])] #Se espera el estado inicial.

FPS=10

start = utime.ticks_ms()
msg_buf=np.zeros(sensor.width(), dtype=np.int8) #Buffer mensaje a enviar

count= 0;
while(True):
    if (uart.any()):
        state=n_to_state[int(uart.readchar())] #Se le comunica el nuevo estado
    t_elapsed = utime.ticks_diff(utime.ticks_ms(), start)
    if t_elapsed/1000 > (1/FPS):
        start = utime.ticks_ms()
        uart.write(msg_buf)
        utime.sleep_ms(66)#El algoritmo llegaba a correr a 15 FPS.
        count=count+1;
        d,err,tag_found,tag_nmbr,fork_or_merge_passed=emulate_outputs(count);
        gen_next_msg(msg_buf,d,err,tag_found,tag_nmbr,fork_or_merge_passed)


