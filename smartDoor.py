#!usr/bin/env python3

import numpy as np
import cv2
import imutils
import time
import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import twilio
from twilio.rest import Client

print ("All packages imported properly!")


def mask_image(img):
    mask=np.zeros((img.shape[0], img.shape[1]),dtype="uint8")

    pts= np.array([[446,0],[1000,0],[1000,720],[446,720]])
    cv2.fillConvexPoly(mask,pts,255)


    masked=cv2.bitwise_and(img,img,mask=mask)
    gray= imutils.resize(masked,width=200)
    gray=cv2.cvtColor(gray,cv2.COLOR_BGR2GRAY)
    gray= cv2.GaussianBlur(gray,(11,11),0)

    return masked, gray

counter=0

while True:
    counter=counter+1
    print()
    print("---Times through loop since starting: "+str(counter)+"---")
    print()

    command = 'raspistill -w 1000 -h 720 -t 1000 -tl 1000 -o test%0d.jpg'
    os.system(command)
    time.sleep(1)
    
    
    print("Captured 1st and 2nd image")

    test1 = cv2.imread("test0.jpg") 
    test2 = cv2.imread("test1.jpg")
    masked1, gray1 = mask_image(test1)
    masked2, gray2 = mask_image(test2)  

    

    #Compare the two images

    pixel_thres =50
    detector_total=np.uint64(0)
    detector=np.zeros((gray2.shape[0],gray2.shape[1]), dtype="uint8")

    #pixel by pixel comparison

    for i in range(0, gray2.shape[0]):
        for j in range(0,gray2.shape[1]):
            if abs(int(gray2[i,j])-int(gray1[i,j]))> pixel_thres:
                detector[i,j]=255

    #Sum detector array
    detector_total=np.uint64(np.sum(detector))
    print("detector total= "+str(detector_total))

    #time.sleep(2)

    if detector_total>4000:
        print("Someone is at the door")
        #Define a unique video file
        timestr=time.strftime("doorbell-%Y%m%d-%h%M%S")
        command2 = 'raspivid -t 5000 -w 1280 -h 720 -fps 30 -o '+ timestr+ '.h264'
        os.system(command2)
        print("Finished recoridng")
    

        #Write images to files
        cv2.imwrite("gray1.jpg", gray1)
        cv2.imwrite("gray2.jpg", gray2)
        cv2.imwrite("masked1.jpg", masked1)
        cv2.imwrite("masked2.jpg", masked2)
        
        # ------------------------------------Email photos to user----------------------------------------------
        
        smtpUser= "iotprojectgroupe@gmail.com"
        smtpPass="iotproject420"



        #Destination
        toAdd= "iotprojectgroupe@gmail.com"
        fromAdd=smtpUser
        f_time=datetime.now().strftime("%a %d %b @ %H:%M")
        subject="Smart Doorbell Photos from: "+f_time
        msg= MIMEMultipart()
        msg["Subject"]=subject
        msg["From"]=fromAdd
        msg["To"]=toAdd

        msg.preamble="Smart Doorbell Photos from: "+f_time

        #Email Text
        body= MIMEText("Smart Doorbell Photos from: "+f_time)
        msg.attach(body)

        #Attach images test0,test1, gray0,gray1,masked0,masked1
        fp= open('test0.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        fp= open('test1.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        fp= open('gray1.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        fp= open('gray2.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        fp= open('masked1.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)
        fp= open('masked2.jpg', 'rb')
        img=MIMEImage(fp.read())
        fp.close()
        msg.attach(img)

        #Send Email

        s= smtplib.SMTP("smtp.gmail.com",587)

        s.ehlo()
        s.starttls()
        s.ehlo()
        s.login(smtpUser,smtpPass)
        s.sendmail(fromAdd,toAdd, msg.as_string())
        s.quit()

        print("Email Delivered...")
# ------------------------------------Text via twilio----------------------------------------------
        account_sid = "AC76ae8ba9c6602acfd5ec3f1782a8b9ca"
        auth_token="f75195a0cf4fb53aaf5f389a96d2b8c8"

        client=Client (account_sid,auth_token)

        message= client.api.account.messages.create(
            to="",
            from_="",
            body="The Pi was triggered at "+f_time + " To access live camera feed click the folling link <LIVE FEED IP + PORT HERE>"
            )


    else:
        print("Nothing detected")

