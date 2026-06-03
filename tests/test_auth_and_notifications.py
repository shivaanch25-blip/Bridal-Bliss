from app.models import User, Notification


def test_register_and_login(client, app):
    response = client.post('/register', data={
        'username': 'testbride',
        'email': 'testbride@example.com',
        'password': 'testpass',
        'role': 'bride'
    }, follow_redirects=True)
    assert b'Registration successful' in response.data

    response = client.post('/login', data={
        'username': 'testbride',
        'password': 'testpass'
    }, follow_redirects=True)
    assert b'Welcome back, testbride!' in response.data


def test_notifications_view_and_mark_read(client, app):
    login_response = client.post('/login', data={
        'username': 'priya',
        'password': 'priya123'
    }, follow_redirects=True)
    assert b'Welcome back, priya!' in login_response.data

    response = client.get('/notifications')
    assert response.status_code == 200
    assert b'Notifications' in response.data
    assert b'Welcome to Bridal Bliss!' in response.data

    # Mark the first notification as read
    with app.app_context():
        notification = Notification.query.filter_by(user_id=1).first()
        assert notification is not None
        assert not notification.is_read
        response = client.post(f'/notifications/{notification.id}/read', follow_redirects=True)
        assert response.status_code == 200
        assert b'Read' in response.data
        notification = Notification.query.get(notification.id)
        assert notification.is_read
