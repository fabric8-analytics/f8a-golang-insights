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
    json_data = get_json_from_response(response)
    assert json_data == {}, "Empty JSON response expected"


def test_liveness_endpoint(client):
    """Test the liveness probe."""
    response = client.get('/api/v1/liveness')
    assert response.status_code == 200
    json_data = get_json_from_response(response)
    assert json_data == {}, "Empty JSON response expected"


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
