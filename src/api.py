import requests
import json
import time


def post_data(data):
    try:
        url = 'http://localhost:5000/update_eeg'

        current_time = time.time()
        eeg_value = data
        
        data = {
            'x': [current_time],
            'y': [eeg_value]
        }
        
        response = requests.post(url, json=data)
    except Exception:
        print("no hay conn al servidor")
