# from api import request_analyze

# bus_info_1 = "usb-xhci-hcd.0-1"
# bus_info_2 = "usb-xhci-hcd.1-1"
# bus_info_3 = "usb-xhci-hcd.0-2"
# bus_info_4 = "usb-xhci-hcd.1-2"

# request_analyze(bus_info_1)
# request_analyze(bus_info_2)
# request_analyze(bus_info_3)
# request_analyze(bus_info_4)

import os
import tkinter as tk
from tkinter import Label, Canvas
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import signal
from utils.request import POST
from utils.gpio import gpio_signal
from utils.parser import parse_qr_data, parse_qr_response
from threading import Thread

# DISPLAY 환경 변수 설정
os.environ['DISPLAY'] = ':0'

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("공유 보관함 키오스크")
        self.geometry("480x770")
        
        self.label = Label(self)
        self.label.pack()
        
        self.qr_label = Label(self, text="test")
        self.qr_label.pack()

        self.processing_label = Label(self, text="처리 중입니다..")
        self.processing_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.processing_label.lower()

        self.indicator_canvas = Canvas(self, width=20, height=20, bg="white", highlightthickness=0)
        self.indicator_canvas.create_oval(2, 2, 18, 18, fill="green")
        self.indicator_canvas.place(x=10, y=10)  # 좌측 상단에 배치
        
        self.cap = cv2.VideoCapture(0)
        self.processing_request = False
        self.last_decode_time = 0
        self.decode_interval = 4  # QR 코드 디코딩 간격 (초)
        self.decode_trigger = False

        self.update_frame()

    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (800, 480))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.label.imgtk = imgtk # type: ignore
                self.label.configure(image=imgtk) # type: ignore

                if not self.decode_trigger:
                    qr_data = self.decodeBarcode(frame)
                    
                    if qr_data:
                        print(qr_data)
                        self.qr_label.config(text=f"QR Code Data: {qr_data}")
                        self.decode_trigger = True  # 디코딩 중지
                        self.indicator_canvas.place_forget()

                        qrs = parse_qr_data(qr_data)

                        print(qrs)

                        if qrs is not None:
                            self.run_in_thread(
                                POST, 
                                "https://sl.bluewarn.dev/auth/qrkey",
                                data={
                                    "qrKey": qrs[0],
                                    "buildingNumber": qrs[1],
                                    "floorNumber": qrs[2],
                                    "lockerNumber": qrs[3],
                                },
                                callback=lambda result: parse_qr_response(result)
                            )
                        self.after(self.decode_interval * 1000, self.reset_decode_trigger)  # 일정 시간 후 디코딩 재개
                    else:
                        self.qr_label.config(text="")

                if self.decode_trigger:
                    self.indicator_canvas.place_forget()
                else:
                    self.indicator_canvas.place(x=10, y=10)
        except Exception as e:
            print(f"An error occurred: {e}")
                
        self.after(10, self.update_frame)
    
    def decodeBarcode(self, frame):
        qr_res = None
        decoded_objects = decode(frame)
        if decoded_objects:
            for obj in decoded_objects:
                qr_data = obj.data.decode("utf-8")
                qr_res = qr_data
                break
        return qr_res 

    def reset_decode_trigger(self):
        self.decode_trigger = False

    def run_in_thread(self, func, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        
        def wrapper():
            try:
                self.after(0, self.processing_label.lift)
                result = func(*args, **kwargs)
                if callback:
                    self.after(0, callback, result)
            except Exception as e:
                print(f"An error occurred in thread: {e}")
            finally:
                self.after(0, self.processing_label.lower)  # Hide the processing label after the thread completes
        Thread(target=wrapper).start()
    
    def send_gpio_signal(self, locker_number):
        gpio_signal(locker_number)
        print("GPIO 신호가 켜졌습니다.")
        self.after(4000, self.reset_gpio_signal, locker_number)

    def reset_gpio_signal(self, locker_number):
        print("GPIO 신호가 꺼졌습니다.")
        gpio_signal(locker_number, False)
    
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
