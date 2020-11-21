# Color Binary Filter Example
#
# This script shows off the binary image filter. You may pass binary any
# number of thresholds to segment the image by.

import sensor, image, time

sensor.reset()
sensor.set_framesize(sensor.QQVGA)
sensor.set_pixformat(sensor.RGB565)
sensor.skip_frames(time = 2000)
clock = time.clock()

# Use the Tools -> Machine Vision -> Threshold Edtor to pick better thresholds.
green_threshold = (11, 94, -88, -28, -52, 125) # L A B
blue_threshold = (0,100,   -128,127,   -128,0) # L A B

while(True):
    clock.tick()
    img = sensor.snapshot().histeq()
    img.binary([green_threshold])
    #img.erode(1)
    img.dilate(1)
    #print(img.get_pixel(72,115))
    ##print(clock.fps())
    ## Test green threshold
    #for i in range(100):
        #clock.tick()
        #img = sensor.snapshot()
        #img.binary([green_threshold])
        #print(clock.fps())

    ## Test blue threshold
    #for i in range(100):
        #clock.tick()
        #img = sensor.snapshot()
        #img.binary([blue_threshold])
        #print(clock.fps())
