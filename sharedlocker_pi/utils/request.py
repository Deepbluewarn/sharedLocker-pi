import requests

def GET(url, params=None):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTPError가 발생하면 예외를 발생시킵니다.
        
        if response.status_code == 200:
            print("GET 요청 성공")
            print("응답 데이터:", response.text)
        else:
            print("GET 요청 실패")
            print("상태 코드:", response.status_code)
            print("응답 데이터:", response.text if response.text else "No response text")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("상태 코드:", response.status_code)
        print("응답 데이터:", response.text if response.text else "No response text")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return response.text if response.text else None

def POST(url, data=None, json=None, headers=None):
    try:
        response = requests.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()  # HTTPError가 발생하면 예외를 발생시킵니다.
        
        if response.status_code == 200:
            print("POST 요청 성공")
            print("응답 데이터:", response.text)
        else:
            print("POST 요청 실패")
            print("상태 코드:", response.status_code)
            print("응답 데이터:", response.text if response.text else "No response text")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print("상태 코드:", response.status_code)
        print("응답 데이터:", response.text if response.text else "No response text")
    except Exception as err:
        print(f"Other error occurred: {err}")
    return response.text if response.text else None