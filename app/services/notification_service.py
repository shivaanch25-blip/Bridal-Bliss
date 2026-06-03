import logging
from app.models import db, Notification
from app.utils.audit import log_event

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_notification(user_id, message, simulate_sms=True, simulate_email=True):
        notification = Notification(user_id=user_id, message=message, is_read=False)
        db.session.add(notification)
        db.session.commit()

        log_event(
            user_id=user_id,
            action_type='create',
            entity_type='notification',
            entity_id=notification.id,
            details=message[:200]
        )

        # Mock external communication for enterprise-style logging
        if simulate_sms:
            logger.info(f"[MOCK SMS] To:{user_id} Message:{message}")
        if simulate_email:
            logger.info(f"[MOCK EMAIL] To:{user_id} Subject: Bridal Bliss Notification")
        return notification

    @staticmethod
    def notify_booking_status(appointment):
        bride_id = appointment.user_id
        salon_name = appointment.salon.name if appointment.salon else 'your salon'
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

        NotificationService.send_notification(bride_id, msg)
        if appointment.salon and appointment.salon.owner_id:
            owner_msg = f"Appointment status for bride {appointment.user.username if appointment.user else 'user'} on {date} ({slot}) is now: {status}."
            NotificationService.send_notification(appointment.salon.owner_id, owner_msg, simulate_sms=False, simulate_email=True)

    @staticmethod
    def notify_order_status(order):
        bride_id = order.user_id
        order_id = order.id
        status = order.status
        amount = order.total_amount
        msg = f"Thank you! Your order #BB-ORD-{order_id} totaling ₹{amount:,.2f} is SUCCESSFUL and status is now: {status}."
        NotificationService.send_notification(bride_id, msg)
