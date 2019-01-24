"""REST API tests."""
import pytest
import json
import os

os.environ.setdefault("USE_AWS", "False")

import insights_engine.rest_api as rest_api


@pytest.fixture(scope='module')
def client():
    """Create a test client for flask app."""
    with rest_api.app.app.test_client() as c:
        yield c


def get_json_from_response(response):
    """Decode JSON from response."""
    return json.loads(response.data.decode('utf8'))


def test_readiness_endpoint(client):
    """Test the liveness probe."""
    response = client.get('/api/v1/readiness')
    assert response.status_code == 200


def test_readiness_endpoint_wrong_http_method(client):
    """Test the /api/v1/readiness endpoint by calling it with wrong HTTP method."""
    response = client.post('/api/v1/readiness')
    assert response.status_code == 405
    response = client.put('/api/v1/readiness')
    assert response.status_code == 405
    response = client.patch('/api/v1/readiness')
    assert response.status_code == 405
    response = client.delete('/api/v1/readiness')
    assert response.status_code == 405


def test_liveness_endpoint(client):
    """Test the liveness probe."""
    response = client.get('/api/v1/liveness')
    assert response.status_code == 200


def test_liveness_endpoint_wrong_http_method(client):
    """Test the /api/v1/liveness endpoint by calling it with wrong HTTP method."""
    response = client.post('/api/v1/liveness')
    assert response.status_code == 405
    response = client.put('/api/v1/liveness')
    assert response.status_code == 405
    response = client.patch('/api/v1/liveness')
    assert response.status_code == 405
    response = client.delete('/api/v1/liveness')
    assert response.status_code == 405


def test_companion(client):
    """Test the companion recommendation endpoint."""
    data = [
        {
            "package_list": [
                "github.com/gogo/protobuf/proto"
            ],
            "comp_package_count_threshold": 1
        }
    ]
    response = client.post('/api/v1/companion_recommendation',
                           data=json.dumps(data),
                           headers={'content-type': 'application/json'})
    assert response.status_code == 200
