import time
from pyb import UART

# UART 3, and baudrate.
uart = UART(1, 38400)
time.sleep(1000)
uart.write("Hello World!\n")

while(True):

    uart.write("Hello World!\n")
    time.sleep(500)
    if (uart.any()):
        print(uart.readline())
    time.sleep(500)
