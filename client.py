import requests

request_data = {
    "model": "example_model",
    "messages": [
        {"text": "Message 1"},
        {"text": "Message 2"},
        {"text": "Message 3"}
    ]
}

response = requests.post('http://localhost:5000/api/messages', json=request_data)
print(response.json())