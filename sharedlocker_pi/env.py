# 스마트 공유 보관함 키오스크 관련 변수

# 보관함 위치
building_number = 23
floor_number = 8

# 각 보관함에 연결되는 카메라의 USB 인터페이스 이름.
# 보관함 내부 촬영에 사용

locker_cam_bus_info = {
    1: "usb-xhci-hcd.0-1",
    2: "usb-xhci-hcd.1-1",
    3: "usb-xhci-hcd.0-2",
    4: "usb-xhci-hcd.1-2"
}

# GPIO 핀 번호 설정
gpio_pins = {
    1: 17,
    2: 27,
    3: 22,
    4: 10
}
