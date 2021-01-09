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
green_threshold = (0, 100, -128, -30, -128, 127) ##TH de día
blue_threshold = (0,100,   -128,127,   -128,-45) # L A B #TH de noche

min_degree = 0
max_degree = 179

while(True):
    clock.tick()
    img = sensor.snapshot().histeq()
    img.lens_corr(1.8)
    img.binary([green_threshold])
    #l=img.find_lines(roi =[80,100,80,40],threshold = 1000)
    #maxMag=0;
    #for i in range(len(l)):
        #if(l[i].magnitude()>maxMag):
            #maxMag=i;
    #img.draw_line(l[maxMag].line(), color = (255, 0, 0))
    #for l in img.find_lines(roi =[80,100,80,40],threshold = 1000):
        #if (min_degree <= l.theta()) and (l.theta() <= max_degree):

    #img.erode(1)
    #img.dilate(1)
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
