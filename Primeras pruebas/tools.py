from pyb import LED
import utime

red_led=LED(1);
green_led=LED(2);
blue_led=LED(3);

def real_time_check(func, FPS):
    start = time.ticks_ms()
    func()
    t_elapsed = time.ticks_diff(time.ticks_ms(), start)
    if t_elapsed > (1/FPS):
        green_led.off()
        red_led.on()
    else
        green_led.on()
        red_led.off()
