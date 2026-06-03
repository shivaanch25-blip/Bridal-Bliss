from app.models import db, Order, OrderItem, Product
from app.utils.audit import log_event
from app.services.notification_service import NotificationService


class OrderService:
    @staticmethod
    def create_order(user_id, cart_items, shipping_address, phone, payment_method):
        subtotal = 0.0
        for product, qty in cart_items:
            subtotal += product.price * qty

        gst = round(subtotal * 0.18, 2)
        total = round(subtotal + gst, 2)

        order = Order(
            user_id=user_id,
            status='Paid',
            total_amount=total,
            gst_amount=gst,
            shipping_address=shipping_address,
            phone=phone,
            payment_method=payment_method,
            payment_status='Paid'
        )
        db.session.add(order)
        db.session.commit()

        for product, qty in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=qty,
                price=product.price
            )
            db.session.add(order_item)
        db.session.commit()

        NotificationService.notify_order_status(order)
        log_event(
            user_id=user_id,
            action_type='create',
            entity_type='order',
            entity_id=order.id,
            details=f'items={len(cart_items)}, total={total}'
        )
        return order
