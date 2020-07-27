import cv2

cap = cv2.VideoCapture('Videos/Fork 640x480.mp4')
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        cv2.imshow('Frame', frame)
        cv2.waitKey(33)
    else:
        break
cap.release()
cv2.destroyAllWindows()
