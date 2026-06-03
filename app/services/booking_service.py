from app.models import db, Appointment, Salon
from app.utils.audit import log_event
from app.services.notification_service import NotificationService


class BookingService:
    @staticmethod
    def create_booking(user_id, salon_id, look_id, appointment_date, time_slot, home_service, total_price, notes):
        salon = Salon.query.get_or_404(salon_id)
        booking = Appointment(
            user_id=user_id,
            salon_id=salon.id,
            look_id=look_id if look_id else None,
            appointment_date=appointment_date,
            time_slot=time_slot,
            home_service=home_service,
            total_price=total_price,
            notes=notes,
            status='Pending'
        )
        db.session.add(booking)
        db.session.commit()

        log_event(
            user_id=user_id,
            action_type='create',
            entity_type='appointment',
            entity_id=booking.id,
            details=f'salon_id={salon_id}, look_id={look_id}, appointment_date={appointment_date}'
        )
        return booking

    @staticmethod
    def update_status(booking, action):
        previous_status = booking.status
        if action == 'confirm':
            booking.status = 'Confirmed'
        elif action == 'reject':
            booking.status = 'Cancelled'
        elif action == 'complete':
            booking.status = 'Completed'
        else:
            return booking
        db.session.commit()
        NotificationService.notify_booking_status(booking)
        log_event(
            user_id=booking.user_id,
            action_type='update',
            entity_type='appointment',
            entity_id=booking.id,
            details=f'{previous_status} -> {booking.status}'
        )
        return booking
