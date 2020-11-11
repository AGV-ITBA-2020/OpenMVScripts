 # Hello World Example
#
# Welcome to the OpenMV IDE! Click on the green run arrow button below to run the script!

import sensor, image, time, pyb

sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(sensor.GRAYSCALE) # Set pixel format to RGB565 (or GRAYSCALE)
sensor.set_framesize(sensor.VGA)   # Set frame size to QVGA (320x240)
#sensor.set_windowing((640, 80))
sensor.skip_frames(time = 500)     # Wait for settings take effect.
clock = time.clock()                # Create a clock object to track the FPS.
green_led=pyb.LED(2);

while(True):
    #pyb.delay(100)
    clock.tick()                    # Update the FPS clock.
    img = sensor.snapshot()         # Take a picture and return the image.
    hist=img.get_histogram()
    th=hist.get_threshold()
    #img.binary([(th,255)])
    printf("Hola")
    green_led.toggle()
    print(clock.fps())              # Note: OpenMV Cam runs about half as fast when connected
                                    # to the IDE. The FPS should increase once disconnected.
