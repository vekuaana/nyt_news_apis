import requests

base_url = "http://localhost:8000/"


def test_health_check():
    response = requests.get(base_url + 'health')
    assert response.status_code == 200
    assert response.json()['status'] == "healthy"
