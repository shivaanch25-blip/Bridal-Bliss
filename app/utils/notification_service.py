from flask import current_app
from app.models import db, Notification

def send_notification(user_id, message, simulate_sms=True, simulate_email=True):
    """
    Saves notification to database and simulates Email/SMS triggers.
    """
    # 1. DB Save
    notif = Notification(user_id=user_id, message=message, is_read=False)
    db.session.add(notif)
    db.session.commit()

    # 2. Mock external communication logs
    if simulate_sms:
        current_app.logger.info(f"[MOCK SMS] To:{user_id} Message:{message}")
    if simulate_email:
        current_app.logger.info(f"[MOCK EMAIL] To:{user_id} Subject: Bridal Bliss Styling Alert")
    return notif

def notify_booking_status(appointment):
    """
    Triggers customized alerts based on booking updates.
    """
    bride_id = appointment.user_id
    salon_name = appointment.salon.name
    date = appointment.appointment_date
    slot = appointment.time_slot
    status = appointment.status
    
    if status == 'Pending':
        msg = f"Your appointment request at '{salon_name}' for {date} ({slot}) is registered and awaiting owner approval."
    elif status == 'Confirmed':
        msg = f"Good news! Your appointment at '{salon_name}' for {date} ({slot}) has been CONFIRMED by the owner."
    elif status == 'Completed':
        msg = f"Your bridal makeover styling session at '{salon_name}' on {date} is marked as COMPLETED. We hope you loved it!"
    elif status == 'Cancelled':
        msg = f"Alert: Your appointment request at '{salon_name}' for {date} has been CANCELLED."
    else:
        msg = f"Your appointment at '{salon_name}' has updated to status: {status}."

    send_notification(bride_id, msg)
    
    # Notify salon owner too!
    owner_id = appointment.salon.owner_id
    owner_msg = f"Appointment status for bride {appointment.user.username} on {date} ({slot}) is now: {status}."
    send_notification(owner_id, owner_msg, simulate_sms=False, simulate_email=True)

def notify_order_status(order):
    """
    Triggers alerts when shopping orders are checked out.
    """
    bride_id = order.user_id
    order_id = order.id
    status = order.status
    amount = order.total_amount
    
    msg = f"Thank you! Your order #BB-ORD-{order_id} totaling ₹{amount:,.2f} is SUCCESSFUL and status is now: {status}."
    send_notification(bride_id, msg)
