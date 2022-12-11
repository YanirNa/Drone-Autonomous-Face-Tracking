from djitellopy import tello
import cv2
import numpy as np
import time

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 25, 0 )
time.sleep(1)




w,h =360,240 #width & hight
fbRange = [6200,6800] # values of frame limit
pid = [0.6,0.6,0]#Proportional-integral-derivative
pError = 0

def findFace(img):#Function that detect faces
     faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")#It is a machine learning based approach where a cascade function is trained from a lot of positive and negative images. It is then used to detect objects in other images. Here we will work with face detection.
     imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)#TURNING IMG TO GRAY IMAGE
     faces = faceCascade.detectMultiScale(imgGray,1.2,7)#Parameter that detect faces with our image
     myFaceListC = []#information for center point
     myFaceListArea = []#for multiple faces to detect the biggest

     for(x,y,w,h) in faces:#when detect faces return us those parameters
         cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)#this loop we create a rectangle around the face
         cx = x+w//2
         cy = y+h//2
         area = w*h 
         cv2.circle(img,(cx,cy),5,(0,255,0),cv2.FILLED)#create a circle around the center
         myFaceListC.append([cx,cy])
         myFaceListArea.append(area)
     if len(myFaceListArea)!=0:
         i=myFaceListArea.index(max(myFaceListArea))#find the biggest area of the face on img
         return img,[myFaceListC[i],myFaceListArea[i]]#and return it
     else:
         return img , [[0,0],0]#cx=0 cy=0 area=0 return nothing
        

def trackFace( info,w,pid,pError ): #function to track the after we found it
    area = info[1]
    x,y =info [0]
    fb = 0
    error =x-w//2
    speed=pid[0]*error+pid[1]*(error-pError)
    speed=int(np.clip(speed,-100,100))


    if area > fbRange[0] and area < fbRange[1]:#holdstill- drone at the ////////point
        fb =  0

    elif area >fbRange[1]:#if its too close move backward
        fb = -20

    elif area < fbRange[0] and area != 0:#if the drone its too far go forward//area != 0 for the case with no face at all
        fb= 20

    #print(speed,fb)

    if x==0:
        speed=0
        error=0

    me.send_rc_control(0,fb,0,speed,)
    return error




#cap = cv2.VideoCapture(0)
while True:
    #_, img = cap.read()
    img = me.get_frame_read().frame
    img = cv2.resize(img,(w,h))
    img, info = findFace(img)#return the image and cx.. as an info
    pError = trackFace(info,w,pid,pError)
    #print("Center", info[0], "Area", info[1])
    cv2.imshow("Output",img)
    if cv2.waitKey(1) & 0xFF ==  ord('q'):
        me.land()
        break
