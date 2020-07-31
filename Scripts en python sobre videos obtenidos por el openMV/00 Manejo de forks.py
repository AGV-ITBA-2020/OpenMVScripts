import cv2
import numpy as np
from copy import deepcopy

def process_multipath(img):
    img_array=img[:, :, 0]
    img_derived_h= np.diff(img_array)
    center_of_lines=list();
    for i in range(np.shape(img_array-1),-1,-1):
        h_borders=np.nonzero(img_derived_h[i,:])# Faltaa
        

def simple_distance_error(img, case):
    first_row = img[-1, :, 0] ##Me quedo con la columna de pixeles más cercana al vehículo
    center_pixel=len(first_row)/2
    prev=0;
    line_borders=[]
    for i in range(len(first_row)):
        if (prev==0 and first_row[i]==255) or (prev==255 and first_row[i]==0) or (i==len(first_row-1) and first_row[i]==1):
            line_borders.append(i)
    line_centers=[]
    for i in range(int(len(line_borders)/2)):
        line_centers.append((line_borders[i*2]+line_borders[i*2]+1)/2)

    if case=="Normal":
        d=center_pixel-line_centers[0]
    elif case=="ForkL":
        d = center_pixel - line_centers[0]
    elif case == "ForkR":
        d = center_pixel - line_centers[-1]
    elif case == "Merge":
        d = line_centers[np.argmin(abs(center_pixel - line_centers[0]))]

    return d;
cap = cv2.VideoCapture('Videos/Fork 640x480.mp4')

orig_frames=[];
while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        #orig_frames.append(cv2.rotate(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.ROTATE_90_COUNTERCLOCKWISE))
        orig_frames.append(cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE))
    else:
        break

proc_frames=deepcopy(orig_frames);
for i in range(len(orig_frames)):
    _,im_bin = cv2.threshold(cv2.cvtColor(orig_frames[i], cv2.COLOR_BGR2GRAY),80,255,cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(im_bin, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contour_areas=[]
    for j in contours:
        contour_areas.append(cv2.contourArea(j))
    line_contour=contours.pop(np.argmax(contour_areas))

    cv2.fillPoly(proc_frames[i], contours, color=(255, 255, 255))
    _, proc_frames[i] = cv2.threshold(cv2.cvtColor(proc_frames[i], cv2.COLOR_BGR2GRAY), 80, 255, cv2.THRESH_BINARY_INV)
    proc_frames[i] = cv2.cvtColor(proc_frames[i],cv2.COLOR_GRAY2BGR)

    d=simple_distance_error(proc_frames[i],"Normal")






    #cv2.drawContours(proc_frames[i], contours, -1,(255,255,255),0)


for i in range(len(orig_frames)):
    concat=cv2.hconcat([np.asarray(orig_frames[i]), np.asarray(proc_frames[i])])
    cv2.imshow('Frame',concat)
    cv2.waitKey(333)
cap.release()
cv2.destroyAllWindows()
