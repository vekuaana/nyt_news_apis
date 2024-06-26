import json
import requests
import pytest
import os

from dotenv import load_dotenv, find_dotenv

base_url = "http://localhost:8005/"
load_dotenv(find_dotenv())


@pytest.fixture
def token():
    response = requests.post(
        url=base_url + "get_token",
        data={
            "username": os.getenv('USER1'),
            "password": os.getenv('PASSWORD1')
        }
    )
    token = response.json()['access_token']
    return token


def test_health_check():
    # Test health check endpoint
    response = requests.get(base_url + 'health')
    assert response.status_code == 200
    assert response.json()['status'] == "healthy"


def test_get_polarity(token):
    # Test polarity endpoint
    data = {
        'abstract': 'The new policy is one of the most significant actions to protect immigrants in years. It affects '
                    'about 500,000 people who have been living in the United States for more than a decade.',
        'headline': 'Biden Gives Legal Protections to Undocumented Spouses of U.S. Citizens',
        'keywords': [
            'Biden, Joseph R Jr',
            'Obama, Barack',
            'Trump, Donald J',
            'United States Politics and Government',
            'Immigration and Emigration',
            'Deferred Action for Childhood Arrivals',
            'Citizenship and Naturalization'
        ],
        'pub_date': '2024-06-18 05:03:07',
        'document_type': 'Article',
        'section_name': 'U.S.',
        'byline': [
            'By Zolan Kanno-Youngs, Miriam Jordan, Jazmine Ulloa and Hamed Aleaziz'
        ],
        'web_url': 'https://www.nytimes.com/2024/06/18/us/politics/biden-legal-protections-undocumented-spouses.html',
        'uri': 'nyt://article/a057ddda-e9c3-56c0-9121-1c04de1f1ac6',
        'main_candidate': [
            'Biden',
            'Trump'
        ],
        'polarity': None,
        'recommended_book': None,
        'election_id': 44,
        'lead_paragraph': None}

    request_body = json.dumps(data)
    res = requests.post(base_url + 'polarity', data=request_body, headers={"Authorization": "Bearer " + token})
    res_json = res.json()['response']
    res_biden = [x for x in res_json if x['entity'] == 'Biden']

    assert res.status_code == 200
    assert res_biden == [{'entity': 'Biden', 'prediction': 'positive'}]
