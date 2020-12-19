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
# DE Día el th green_threshold = (11, 94, -88, -28, -52, 125) # L A B
green_threshold = (0, 100, -128, -32, -128, 127) # L A B
blue_threshold = (0,100,   -128,127,   -128,-20) # L A B
tag_families = 0 | image.TAG36H11 # Familia de tags a identificar

while(True):
    clock.tick()
    img = sensor.snapshot().histeq()
    #img = sensor.snapshot().histeq()
    #copyImg = img.copy();
    #img.lens_corr(1.8)
    ##img = image.rgb_to_lab(img)
    ##th = img.histogram().get_threshold()
    ##print(th)
    img.binary([green_threshold])
    ##img = sensor.snapshot().histeq()
    ##for tag in img.find_apriltags(families=tag_families): # defaults to TAG36H11 without "families".
        ##print_args = (tag.id(), (180 * tag.rotation()) / 3.1415)
        ##print("Tag ID %d, rotation %f (degrees)" % print_args)
    #img.binary([green_threshold])
    #img.erode(1)
    #img.dilate(2)

    #print(img.get_pixel(72,115))
    ##print(clock.fps())
    ## Test green threshold
    #for i in range(100):
        #clock.tick()
        #img = sensor.snapshot()
        #img.binary([green_threshold])
        #print(clock.fps())

    print(clock.fps())
