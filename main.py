from tkinter import *
from tkinter import ttk
import threading
import serial
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
#ap = argparse.ArgumentParser()
#ap.add_argument("-c", "--cascade", required=True,
#	help = "path to where the face cascade resides")
#ap.add_argument("-e", "--encodings", required=True,
#	help="path to serialized db of facial encodings")
#args = vars(ap.parse_args())

class App:
    def __init__(self,master):
        self.master=master
        self.st='nothing'
        self.lcd_state='nothing'
        self.closed=False
        self.authenticate_tvar=StringVar()
        #self.lcd =serial.Serial(port="/dev/ttyACM0", baudrate= 115200, timeout=1)
        #self.motor=serial.Serial(port='/dev/ttyACM0', baudrate=115200, timeout=.1)
        self.lcdDisplay("Welcome:Register to begin")
        self.streamStarted=False
        self.header=Frame(master,width=800,height=300)
        self.header.grid(columnspan=3,rowspan=4,row=0)
        self.authenticate_btn=Button(master,textvariable=self.authenticate_tvar,height=1,
                    command=self.startautheticate,width=15,)
        self.authenticate_btn.grid(row=0,column=1,)
        
        self.startEngine_btn=Button(master,text="Start Engine",height=1,
                                    command=self.startengine,width=15,state='disabled')
        self.stopEngine_btn=Button(master,text="Stop Engine",height=1,
                    command=self.stopengine,width=15,state='disabled')
        self.stopEngine_btn.grid(row=3,column=1,)
        self.startEngine_btn.grid(row=2,column=1,)
        self.authenticate_tvar.set('Begin Authenication')
        self.master.protocol("WM_DELETE_WINDOW", self.close)
    def startautheticate(self):
        print("key pressed")
        self.authenticate_btn.configure(state='disabled')
        self.lcd.write(bytes("Please Face Cam:To Authenticate", 'utf-8'))
        self.st='starting stream'
        self.authenticate_tvar.set("Authenticating")
        if not (self.streamStarted):
            threading.Thread(target=self.authenticate).start()
    def lcdDisplay(self,data):
        self.lcd =serial.Serial(port="/dev/ttyACM0", baudrate= 115200, timeout=1)
        self.lcd.write(bytes(data, 'utf-8'))
    def motorRun(self):
        print("starting motor")
        self.motor=serial.Serial(port='/dev/ttyACM1', baudrate=115200, timeout=.1)
        self.motor.write(bytes("1", 'utf-8'))
        time.sleep(0.05)
        print(self.motor.readline())
        time.sleep(2)
    def motorStop(self):
        self.motor=serial.Serial(port='/dev/ttyACM1', baudrate=115200, timeout=.1)
        self.motor.write(bytes("0", 'utf-8'))
        time.sleep(0.05)
        print(self.motor.readline())
        time.sleep(2) 
    def startengine(self):
        self.motorRun()
        self.startEngine_btn.configure(state='disable')
        self.stopEngine_btn.configure(state='active')
    def stopengine(self):
        self.motorStop()
        self.lcd_state='nothing'
        self.startEngine_btn.configure(state='disable')
        self.stopEngine_btn.configure(state='disable')
    def close(self):
        self.motorStop()
        self.closed=True
        self.master.destroy()
    def authenticate(self):
        self.streamStarted=True
        print("[INFO] loading encodings + face detector...")
        data = pickle.loads(open("encodings.pickle", "rb").read())
        detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        self.lcdDisplay("AWIATING:AUTHORISATION..")
        #vs = VideoStream(src=0).start()
        vs = VideoStream(usePiCamera=True).start()
        time.sleep(2.0)
        # start the FPS counter
        fps = FPS().start()

        # loop over frames from the video file stream
        while True:
            # grab the frame from the threaded video stream and resize it
            # to 500px (to speedup processing)
            frame = vs.read()
            frame = imutils.resize(frame, width=500)
            
            # convert the input frame from (1) BGR to grayscale (for face
            # detection) and (2) from BGR to RGB (for face recognition)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # detect faces in the grayscale frame
            rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                minNeighbors=5, minSize=(30, 30))
            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []
            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                    encoding,tolerance=0.4)
                name = "Unknown"
                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                
                # update the list of names
                names.append(name)
                    # loop over the recognized faces
            
         
            
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image
                if(name =="Unknown" and self.lcd_state!='detectedalready'):
                    detail="*UNAUTHORISED*"
                    threading.Thread(target=self.lcdDisplay,args=(detail,)).start()
                elif(name!="Unknown" and self.lcd_state!='detectedalready'):
                    self.lcd_state='detectedalready'
                    detail='{}:Confirm Welcome'.format(name)
                    threading.Thread(target=self.lcdDisplay,args=(detail,)).start()
                    self.startEngine_btn.configure(state='active')
                cv2.rectangle(frame, (left, top), (right, bottom),
                    (0, 255, 0), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (0, 255, 0), 2)
            # display the image to our screen
            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if self.closed:
                print("left")
                break
            # update the FPS counter
            fps.update()
        fps.stop()
        print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
        # do a bit of cleanup
        cv2.destroyAllWindows()
        vs.stop()
                
       
root=Tk()
root.geometry('+%d+%d'%(350,10))
def on_closing():
    lcd =serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)
    lcd.write(bytes("Registration: Done", 'utf-8'))
    root.destroy()
app=App(root)
root.mainloop()