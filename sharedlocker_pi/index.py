# from api import request_analyze

# bus_info_1 = "usb-xhci-hcd.0-1"
# bus_info_2 = "usb-xhci-hcd.1-1"
# bus_info_3 = "usb-xhci-hcd.0-2"
# bus_info_4 = "usb-xhci-hcd.1-2"

# request_analyze(bus_info_1)
# request_analyze(bus_info_2)
# request_analyze(bus_info_3)
# request_analyze(bus_info_4)

import tkinter as tk
from tkinter import Label
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import requests
import time
import signal
import RPi.GPIO as GPIO

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Camera Feed")
        self.geometry("800x600")
        
        self.label = Label(self)
        self.label.pack()
        
        self.qr_label = Label(self, text="")
        self.qr_label.pack()
        
        self.cap = cv2.VideoCapture(0)
        self.processing_request = False
        self.last_decode_time = 0
        self.decode_interval = 4  # QR 코드 디코딩 간격 (초)

        # GPIO 설정
        self.gpio_pin = 17  # 사용할 GPIO 핀 번호
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)

        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk
            self.label.configure(image=imgtk)

            qr_data = self.decodeBarcode(frame)
            print(qr_data)
            if qr_data:
                self.send_request(qr_data)
                self.send_gpio_signal()

        self.after(10, self.update_frame)
    
    def decodeBarcode(self, frame):
        current_time = time.time()
        qr_res = None
        if not self.processing_request and (current_time - self.last_decode_time) > self.decode_interval:
            decoded_objects = decode(frame)
            if decoded_objects:
                for obj in decoded_objects:
                    qr_data = obj.data.decode("utf-8")
                    self.qr_label.config(text=f"QR Code Data: {qr_data}")
                    qr_res = qr_data
                    break  # Only show the first detected QR code
            else:
                self.qr_label.config(text="")  # Reset label if no QR code is detected
            self.last_decode_time = current_time
        
        return qr_res  # Return None if no QR code is detected

    def send_request(self, qr_data):
        self.processing_request = True
        print(time.time())
        try:
            response = requests.get(f"http://example.com/api?data={qr_data}")
            if response.status_code == 200:
                print("Request successful:", response.text)
            else:
                print("Request failed:", response.status_code)
        except Exception as e:
            print("Error during request:", e)
        finally:
            self.processing_request = False

    def send_gpio_signal(self):
        GPIO.output(self.gpio_pin, GPIO.HIGH)
        time.sleep(4)  # 1초 동안 신호를 유지
        GPIO.output(self.gpio_pin, GPIO.LOW)
    
    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == '__main__':
    app = MainWindow()

    def sigint_handler(sig, frame):
        app.quit()
        app.update()
    signal.signal(signal.SIGINT, sigint_handler)

    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
