from tkinter import *
from tkinter import ttk
from imutils import paths
import threading
import serial
import time
import os
import face_recognition
import pickle
import cv2
from picamera import PiCamera
from picamera.array import PiRGBArray
################Capture################
class App:
    def __init__(self,master):
        self.master=master
        self.st='nothing'
        self.lcd =serial.Serial(port="/dev/ttyACM0", baudrate= 115200, timeout=1)
        self.lcd.write(bytes("Welcome:Register to begin", 'utf-8'))
        self.register_tvar=StringVar()
        self.name_tvar=StringVar()
        self.header=Frame(master,width=800,height=300)
        self.header.grid(columnspan=3,rowspan=5,row=0)
        self.register_btn=Button(master,textvariable=self.register_tvar,height=1,
                    command=self.register,width=15,)
        self.register_btn.grid(row=1,column=0,)

        self.name_edit=Entry(master,width=15,textvariable=self.name_tvar,state='disabled')
        self.name_edit.grid(row=1,column=1)

        self.takePicture_btn=Button(master,text="Take Picture",height=1,
                    command=self.takePic,width=15,state='disabled',)
        self.takePicture_btn.grid(row=1,column=2,)

        #self.authentication_btn=Button(master,text="Start Engine",height=1,
          #          command=self.authenticate,width=15)
        #self.authentication_btn.grid(row=3,column=1)

        self.compile_btn=Button(master,text='Compile Images',height=1,
                command=self.startencoding,width=15)
        self.compile_btn.grid(row=4,column=1)
        self.register_tvar.set("Start Registration")
        self.name_edit.bind('<Return>',self.nameentered)
        
        
    def register(self):
        print('Button register')
        self.lcd.write(bytes("Enter Name:In Text field", 'utf-8'))
        self.name_edit.configure(state='normal')
        self.register_btn.configure(state='disable')
       # self.authentication_btn.configure(state='disable')
        #self.stop_btn.configure(state='disable')
    def takePic(self):
        self.st='capture'
        print(self.st)
    def lcdhandler(self,data):
        self.lcd.write(bytes(data, 'utf-8'))
    def startencoding(self):
        self.compile_btn.configure(state='disable')
        self.register_btn.configure(state='disable')
        self.lcd.write(bytes("Encoding :starting...", 'utf-8'))
        imagePaths = list(paths.list_images("dataset"))
        knownEncodings = []
        knownNames = []
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
            #data_="processing image {}/{}".format(i + 1,
                
            #self.lcd.write(bytes("data_", 'utf-8'))
            name = imagePath.split(os.path.sep)[-2]
            # load the input image and convert it from BGR (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                model="hog")
            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)
            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)
                
        # dump the facial encodings + names to disk
        print("serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("encodings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()
        print("done")
        self.lcd.write(bytes("Encoding :Done", 'utf-8'))
        self.compile_btn.configure(state='active')
        self.register_btn.configure(state='active')
    def nameentered(self,*args):
        name=self.name_tvar.get()
        self.name_edit.configure(state='disable')
        self.takePicture_btn.configure(state='active')
        self.name_tvar.set("")
        self.lcd.write(bytes("Face Camera", 'utf-8'))
        if not os.path.exists("dataset/"+ name):
            os.makedirs("dataset/"+ name)
        
        threading.Thread(target=self.capture,args=(name,)).start()
    
    def capture(self,name):
        print(name)
        cam = PiCamera()
        cam.resolution = (512, 304)
        cam.framerate = 10
        rawCapture = PiRGBArray(cam, size=(512, 304))
        img_counter = 0
        while True:
            for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                image = frame.array
                cv2.imshow("Hit Take Picture", image)
                rawCapture.truncate(0)
                k = cv2.waitKey(1)
                rawCapture.truncate(0)
                if img_counter>=10:
                    self.takePicture_btn.configure(state='disable')
                    self.name_edit.configure(state='disable')
                    self.register_btn.configure(state='disable')
                    break
                elif self.st=='capture':
                    # SPACE pressed
                    img_name = "dataset/"+ name +"/image_{}.jpg".format(img_counter)
                    cv2.imwrite(img_name, image)
                    data="{} :Image {}/10 Taken".format(name,img_counter+1)
                    self.lcd.write(bytes(data, 'utf-8'))
                    img_counter += 1
                    if img_counter>=10:
                        self.lcd.write(bytes("Registation:Succesful", 'utf-8'))
                    self.st='nothing'
            break
        cv2.destroyAllWindows()
        self.lcd.write(bytes("Done....", 'utf-8'))
        self.st ='nothing'
        cam.close()
        self.lcd.write(bytes("Done....", 'utf-8'))
        
        


#######################################
root=Tk()
root.geometry('+%d+%d'%(350,10))
app=App(root)
def on_closing():
    lcd =serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)
    lcd.write(bytes("Registration: Done", 'utf-8'))
    root.destroy()
lcd =serial.Serial(port="/dev/ttyACM0", baudrate=115200, timeout=1)
lcd.write(bytes("Registration: Done", 'utf-8'))
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

