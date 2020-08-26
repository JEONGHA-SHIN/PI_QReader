import pyzbar.pyzbar as pyzbar
from threading import *
import cv2
import server
import image_server
import time
import socket

class QReader:
    def __init__(self):
        self.s = server.ServerSocket()
        self.i_s = image_server.ImageServer()

        
        ip = socket.gethostbyname("raspberrypi.local")
        print(ip)

        self.s.start(ip, 9292)
        self.i_s.start(ip,9293)

    def detectQR(self):
        text = "waiting...\n"
        pre_text = ""
        pre_time = 0
        self.cap = cv2.VideoCapture(0)
        while(self.cap.isOpened()):
            ret, img = self.cap.read()

            if not ret:
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
     
            decoded = pyzbar.decode(gray)
            if decoded != []:
                for d in decoded: 
                    x, y, w, h = d.rect

                    barcode_data = d.data.decode("utf-8")
                    barcode_type = d.type
                    #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    text = str(barcode_data)
                    print(text)

                if pre_text != text:
                    self.s.send(text)
                    self.i_s.send(img)
                    print("sending...",text)
                    pre_text = text
                pre_time = time.time()

            else:
                if time.time() - pre_time > 3:
                    text = "waiting...\n"
                    if pre_text != text:
                        self.s.send(text)
                        self.i_s.send(img)
                        print("sending...",text)
                        pre_text = text
                    pre_time = time.time()
                print(time.time() - pre_time)

                #cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
            #cv2.imshow('img', img)

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
            #time.sleep(0.5)

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
        self.s.stop()
        self.i_s.stop()

if __name__ == "__main__":
    Q = QReader()
    Thread(target=Q.detectQR(), args=())

