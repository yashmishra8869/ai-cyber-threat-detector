from app import create_app


def test_health_endpoint_response():
    app = create_app()
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    payload = response.get_json()
    assert 'status' in payload
    assert 'model_ready' in payload
