import cv2
import numpy as np
from copy import deepcopy

cap = cv2.VideoCapture('../Videos seguimiento camino/Piso marcos 1.mp4')


orig_frames=[];
while cap.isOpened():
    ret, frame = cap.read()
    if ret == True:
        #orig_frames.append(cv2.rotate(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), cv2.ROTATE_90_COUNTERCLOCKWISE))
        #orig_frames.append(cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE))
        orig_frames.append(frame);
    else:
        break


proc_frames=deepcopy(orig_frames);
kernel = np.zeros((20,20),np.float32)
# kernel[1][0]=-1;
# kernel[1][2]=1;
kernel[9:12,7:14]=1;
kernel[9:12,0:7]=-1;
kernel[9:12,14:20]=-1;
kernel=kernel/20;

def applyKernelMode1(proc_frame):
    auxArray = np.array(proc_frame, np.float32) - 160  # Paso los valores a floats para que <0 negro, >0 blanco
    A = cv2.filter2D(auxArray, -1, kernel)  # Correlaciono con forma de línea
    # A=A-np.min(A) #Lo paso a numeros positivos
    # A=A*255/np.max(A) #Que vaya entre 0 y 255
    _, proc_frame = cv2.threshold(A, 240, 255, cv2.THRESH_BINARY)
    proc_frame = np.array(proc_frame, np.uint8);
    return proc_frame;
def applyKernelMode2(proc_frame):
    _, proc_frame = cv2.threshold(proc_frame, 160, 255, cv2.THRESH_BINARY)
    return proc_frame;

for i in range(len(orig_frames)):
    proc_frame = cv2.cvtColor(proc_frames[i], cv2.COLOR_BGR2GRAY) #Paso a greyscale
    proc_frame= cv2.equalizeHist(proc_frame)                #Eq Hist para mayor contraste
    #proc_frame = applyKernelMode1(proc_frame)
    proc_frame = applyKernelMode1(proc_frame)
    proc_frames[i] = cv2.cvtColor(proc_frame,cv2.COLOR_GRAY2BGR)
for i in range(len(orig_frames)):
    #concat=cv2.hconcat(orig_frames[i],proc_frames[i]) #No entiendo por qué estalla, antes no lo hacía
    concat = np.concatenate((orig_frames[i], proc_frames[i]), axis=1)
    imF = cv2.resize(concat, (1000, 250))
    cv2.imshow('Frame',imF)
    cv2.waitKey(50)
cap.release()
cv2.destroyAllWindows()