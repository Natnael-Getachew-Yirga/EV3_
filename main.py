from multiprocessing.connection import wait
import torch
import numpy as np
import cv2
import math
import time
import paho.mqtt.client as mqtt

temp1=1000
last_save_time = time.time()

client = mqtt.Client()
client.connect("192.168.137.3",1883,60)

CM_TO_PIXELW=0.059
CM_TO_PIXELL=0.057

# Model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='last.pt')#, force_reload=True




cap = cv2.VideoCapture(1)
while cap.isOpened():
    ret, frame = cap.read()
    frame = cv2.resize(frame, (640, 480), fx = 0, fy = 0,
                         interpolation = cv2.INTER_CUBIC)
  
    model.conf=0.7
    results = model(frame)
    img=np.squeeze(results.render())
    
  
    for box in results.xyxy[0]:
       
        xmin = int(box[0])
        ymin = int(box[1])
        xmax = int(box[2])
        ymax = int(box[3])
        print(xmin,ymin,xmax,ymax,float(box[4]),box[5])

# Draw circle in the center of the bounding box
        x2 = int(xmin + ((xmax-xmin)/2))
        y2 = int(ymin + ((ymax-ymin)/2))
        
        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        pixel_center = hsv_frame[y2, x2]
        hue_value = pixel_center[0]
        lvalue=pixel_center[2]
        color = "Undefined"
        if  hue_value < 5:
            color = "RED"
        elif hue_value < 22:
            color = "ORANGE"
        elif hue_value < 33:
            color = "YELLOW"
        elif hue_value < 90:
            color = "GREEN"
        elif hue_value < 131:
            color = "BLUE"
        elif lvalue==0:
            color = "black"
        pixel_center_bgr = img[y2, x2]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])
   
        cv2.putText(img, color, (x2 - 200, 100), 0, 1.5, (b, g, r), 5)
        cv2.circle(img, (x2, y2), 5, (25, 25, 25), 3)
        cv2.imshow('img',img)

        x2_cm = x2 * CM_TO_PIXELW
        y2_cm = y2 * CM_TO_PIXELL
        #print(x2_cm,y2_cm)
        if (x2_cm>18):
            xb=x2_cm-18
            yb=y2_cm
            t=math.degrees(math.atan(yb/xb))
            t=int(t)
            #print(t)

        else:
            xb=18-x2_cm
            yb=y2_cm
            t=math.degrees(math.atan(yb/xb))
            t=180-t
            t=int(t)
            #print(t)
            
        if (abs(temp1-t)>0.5 and (time.time() - last_save_time) > 5):
            #print(t)
            temp1=t
               
                
        # This is the Publisher
                    
            if (t<180 and t>0 and y2_cm<12): 
                print("publish color")
                client.publish("topic/test", color) 
                print("publish angle")     
                client.publish("topic/test", t)
                last_save_time = time.time()
        
        else:
            cv2.imshow('img',img)           
           
    
        
    cv2.imshow('img',img)   
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
client.disconnect()

##########################






