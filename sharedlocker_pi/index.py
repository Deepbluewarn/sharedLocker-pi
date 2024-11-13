import os
import tkinter as tk
from tkinter import Label, Canvas, Toplevel
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import signal
from utils.request import POST
from utils.gpio import gpio_signal
from utils.parser import parse_qr_data, parse_qr_response
from threading import Thread
from picamera2 import Picamera2
from api import request_analyze

# DISPLAY 환경 변수 설정
os.environ['DISPLAY'] = ':0'

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("공유 보관함 키오스크")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        
        self.label = Label(self)
        self.label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.processing_label = Label(self, text="처리 중입니다..")

        self.indicator_canvas = Canvas(self, width=20, height=20, bg="white", highlightthickness=0)
        self.indicator_canvas.create_oval(2, 2, 18, 18, fill="green")
        self.indicator_canvas.place(x=10, y=10)  # 좌측 상단에 배치

        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (800, 480)}))
        self.picam2.set_controls({"AfMode": 2 ,"AfTrigger": 0})
        self.picam2.start()
        
        self.cap = cv2.VideoCapture(0)
        self.processing_request = False
        self.last_decode_time = 0
        self.decode_interval = 4  # QR 코드 디코딩 간격 (초)
        self.decode_trigger = False

        self.update_frame()

    def update_frame(self):
        try:
            frame = self.picam2.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (1000, 600))
            frame = cv2.flip(frame, 1)
            img = Image.fromarray(frame)

            imgtk = ImageTk.PhotoImage(image=img)
            self.label.imgtk = imgtk # type: ignore
            self.label.configure(image=imgtk) # type: ignore

            if not self.decode_trigger:
                qr_data = self.decodeBarcode(frame)
                
                if qr_data:
                    print(qr_data)
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
                            callback=lambda result: self.qrValidated(result)
                        )
                    self.after(self.decode_interval * 1000, self.reset_decode_trigger)  # 일정 시간 후 디코딩 재개
                else:
                    None
                    # self.qr_label.config(text="")

            if self.decode_trigger:
                self.indicator_canvas.place_forget()
            else:
                self.indicator_canvas.place(x=10, y=10)
        except Exception as e:
            print(f"An error occurred: {e}")
                
        self.after(10, self.update_frame)
    
    def qrValidated(self, result):
        qr_data = parse_qr_response(result)

        if qr_data["success"] is False:
            return
        
        self.show_message('보관함이 열렸습니다.')
        print(qr_data)
        self.send_gpio_signal(qr_data["value"]["lockerNumber"])

        self.run_in_thread(request_analyze, qr_data["value"]["lockerNumber"])

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
                self.after(0, self.show_processing_label)
                result = func(*args, **kwargs)
                if callback:
                    self.after(0, callback, result)
            except Exception as e:
                print(f"An error occurred in thread: {e}")
            finally:
                self.after(0, self.hide_processing_label)  # Hide the processing label after the thread completes
        Thread(target=wrapper).start()
    
    def show_processing_label(self):
        self.processing_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)
    def hide_processing_label(self):
        self.processing_label.place_forget()

    def show_message(self, message):
        # 새로운 Toplevel 창 생성
        message_window = Toplevel(self)
        message_window.geometry("300x100")
        message_window.attributes('-topmost', True)  # 창을 항상 위에 표시

        # 메시지 레이블 생성
        message_label = Label(message_window, text=message, font=("Helvetica", 14))
        message_label.pack(expand=True)

        self.after(4000, message_window.destroy)

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
