from app import create_app


def test_dashboard_has_data_sections():
    app = create_app()
    client = app.test_client()
    response = client.get('/dashboard')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'Cybersecurity Dashboard' in html
    assert 'Model evaluation metrics' in html
