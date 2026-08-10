import requests

def test_api_connection():
    response = requests.get("https://httpbin.org/get", timeout=10)
    assert response.status_code == 200
