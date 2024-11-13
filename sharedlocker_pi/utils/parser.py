import re
import json

def parse_qr_data(qr_data):
    pattern = r'^([a-zA-Z0-9]{8}) (\d+) (\d+) (\d+)$'
    match = re.match(pattern, qr_data)
    
    if match:
        random_str, num1, num2, num3 = match.groups()
        return (random_str, int(num1), int(num2), int(num3))
    else:
        print("Invalid input structure")

def parse_qr_response(qr_res):
    return json.loads(qr_res)
