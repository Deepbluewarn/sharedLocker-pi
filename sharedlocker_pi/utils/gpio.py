import RPi.GPIO as GPIO

# GPIO 핀 번호 설정
gpio_pins = {
    1: 17,  # 사용할 GPIO 핀 번호
    2: 27,  # 사용할 GPIO 핀 번호
    3: 22,  # 사용할 GPIO 핀 번호
    4: 10   # 사용할 GPIO 핀 번호
}

# GPIO 초기화 함수
def init():
    GPIO.setmode(GPIO.BCM)
    for pin in gpio_pins.values():
        GPIO.setup(pin, GPIO.OUT)

def gpio_signal(locker_number, out=True):
    pin = gpio_pins.get(locker_number)
    if pin is not None:
        GPIO.output(pin, GPIO.HIGH if out else GPIO.LOW)
    else:
        print("Invalid locker number")

init()
