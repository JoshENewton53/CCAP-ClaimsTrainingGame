"""Test API endpoint"""
import requests
import json

try:
    response = requests.post(
        'http://localhost:5000/api/death-certificate/generate',
        json={'difficulty': 'medium'}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Keys in response: {list(data.keys())}")
    if 'certificate_pdf' in data:
        print(f"PDF data length: {len(data['certificate_pdf'])}")
    else:
        print("No certificate_pdf in response!")
        print(f"Response: {data}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
