from utils.camera import get_picture
from utils.request import POST

def request_analyze(bus_info):
    encoded_image = get_picture(bus_info)

    if encoded_image is None:
        print("이미지가 없습니다.")
        return

    data_url = f"data:image/jpeg;base64,{encoded_image}"

    post_headers = {'x-api-key': 'token_for_locker'}
    prompt = """
        해당 이미지는 보관함 내부를 촬영한거야. 
        보관함 내부에 어떤 물품이 저장되어 있는지를 문자열로 구성된 배열로 출력해줘. 
        물품에 대한 상세한 내용 보다는 좀 더 넓은 범주의 단어로 출력해야 하고 응답은 대괄호와 쌍따옴표로만 구성되어야 해. (출력 예시: ["연필", "가방", "책", "노트북"])
        만약 사진에 물품이 없는거 같으면 빈 배열을 출력해줘.
    """

    POST(
        "https://sl.bluewarn.dev/api/locker/analyze",
        data={
            "imageUrl": data_url,
            "prompt": prompt,
            "buildingNumber": 1,
            "floorNumber": 1,
            "lockerNumber": 1,
        },
        headers=post_headers
    )