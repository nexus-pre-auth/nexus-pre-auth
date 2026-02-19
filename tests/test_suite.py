import pytest

# Test suite for /v28/analyze endpoint

@pytest.fixture
def client():
    from your_flask_app import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_analyze_success(client):
    response = client.post('/v28/analyze', json={'data': 'sample data'})
    assert response.status_code == 200
    assert 'expected_key' in response.json


def test_analyze_failure(client):
    response = client.post('/v28/analyze', json={'data': ''})
    assert response.status_code == 400  # Bad Request
    assert 'error' in response.json
