import RPi.GPIO as GPIO
import time

# GPIO 설정
gpio_pin = 17 # 사용할 GPIO 핀 번호
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

GPIO.output(gpio_pin, GPIO.HIGH)
time.sleep(10)
GPIO.output(gpio_pin, GPIO.LOW)
