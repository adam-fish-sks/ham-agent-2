import requests
import json
import os
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
WORKWIZE_KEY = os.getenv('WORKWIZE_KEY')

employee_id = '125726'
url = f'https://prod-back.goworkwize.com/api/public/employees/{employee_id}'

headers = {
    'Authorization': f'Bearer {WORKWIZE_KEY}',
    'Content-Type': 'application/json'
}

response = requests.get(url, headers=headers, verify=False)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    if data.get('success') and data.get('data'):
        emp = data['data']
        print(f"\nEmployee ID: {emp.get('id')}")
        print(f"Name: {emp.get('first_name')} {emp.get('last_name')}")
        print(f"Email: {emp.get('email')}")
        print(f"Status: {emp.get('status')}")
    else:
        print("No data found")
else:
    print(f"Error: Status {response.status_code}")
    print(response.text)
