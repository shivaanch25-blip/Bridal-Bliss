from app.models import User, Product, Order, OrderItem


def login_as_bride(client):
    return client.post('/login', data={'username': 'priya', 'password': 'priya123'}, follow_redirects=True)


def test_cart_checkout_and_order_creation(client, app):
    login_response = login_as_bride(client)
    assert b'Welcome back, priya!' in login_response.data

    with client.session_transaction() as session:
        session['cart'] = {'1': 1}

    response = client.post('/shop/payment/simulate', data={
        'shipping_address': '123 Main Street',
        'phone': '9876543210',
        'payment_method': 'TestCard',
        'simulate_status': 'success'
    }, follow_redirects=True)
    assert b'Order placed and payment simulated successfully' in response.data

    with app.app_context():
        order = Order.query.filter_by(user_id=1).first()
        assert order is not None
        assert order.payment_status == 'Paid'
        assert len(order.items) == 1
        assert order.items[0].price == 115000.0
