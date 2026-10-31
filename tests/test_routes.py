from app import create_app


def test_home_page_response():
    app = create_app()
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200


def test_analyze_page_response():
    app = create_app()
    client = app.test_client()
    response = client.get('/analyze')
    assert response.status_code == 200


def test_dashboard_response():
    app = create_app()
    client = app.test_client()
    response = client.get('/dashboard')
    assert response.status_code == 200
