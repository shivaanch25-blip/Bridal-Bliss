import json


def test_api_products_and_looks(client):
    response = client.get('/api/products')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1

    response = client.get('/api/looks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) == 1


def test_api_bookings_requires_login(client):
    response = client.get('/api/bookings')
    assert response.status_code in (302, 401)


def test_api_orders_and_wishlist(client):
    login_response = client.post('/login', data={'username': 'priya', 'password': 'priya123'}, follow_redirects=True)
    assert b'Welcome back, priya!' in login_response.data

    response = client.get('/api/orders')
    assert response.status_code == 200
    orders_payload = json.loads(response.data)
    assert orders_payload['status'] == 'success'
    assert isinstance(orders_payload['data'], list)

    response = client.get('/api/wishlist')
    assert response.status_code == 200
    wishlist_payload = json.loads(response.data)
    assert wishlist_payload['status'] == 'success'
    assert isinstance(wishlist_payload['data'], list)
