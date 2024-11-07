import cv2
import base64
from utils.device import get_device_by_bus_info

def get_picture(bus_info):
    device = get_device_by_bus_info(bus_info)

    if not device:
        print("카메라를 찾을 수 없습니다.")
        return

    # 카메라 장치 열기
    cap = cv2.VideoCapture(device)

    if not cap.isOpened():
        print("카메라를 열 수 없습니다.")
        return

    # 해상도 설정 (예: 1280x720)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # 첫 번째 카메라에서 프레임 읽기
    ret, frame = cap.read()
    
    if ret:
        # 첫 번째 카메라 이미지 파일로 저장
        cv2.imwrite(f'{bus_info}.jpg', frame)
        print("첫 번째 카메라 이미지를 저장했습니다.")

        res, frame_encode = cv2.imencode('.jpg', frame)
        jpg_base64 = base64.b64encode(frame_encode)
        return jpg_base64.decode('utf-8')
    else:
        print("첫 번째 카메라에서 프레임을 읽을 수 없습니다.")

    # 카메라 장치 해제
    cap.release()
    cv2.destroyAllWindows()
