import requests

# GET 요청 보내기
def GET(url, params=None):
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("GET 요청 성공")
        print("응답 데이터:", response.text)
    else:
        print("GET 요청 실패")
        print("상태 코드:", response.status_code)

# POST 요청 보내기
def POST(url, data=None, json=None, headers=None):
    response = requests.post(url, data=data, json=json, headers=headers)
    if response.status_code == 200:
        print("POST 요청 성공")
        print("응답 데이터:", response.text)
    else:
        print("POST 요청 실패")
        print("상태 코드:", response.status_code)
