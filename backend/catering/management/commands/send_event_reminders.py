"""
Section 14: Send Event Reminder Emails via Brevo.
Usage: python manage.py send_event_reminders
Schedule: Run daily via cron or Railway cron job.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from catering.models import CateringEvent, EventReminder


class Command(BaseCommand):
    help = 'Send reminder emails for upcoming events (3 days and 1 day before)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        three_days = today + timedelta(days=3)
        one_day = today + timedelta(days=1)
        
        sent_count = 0

        # 3-day reminders
        events_3day = CateringEvent.objects.filter(
            date=three_days,
            status__in=['confirmed', 'received', 'pending']
        )
        for event in events_3day:
            sent_count += self._send_reminder(event, '3day')

        # 1-day reminders
        events_1day = CateringEvent.objects.filter(
            date=one_day,
            status__in=['confirmed', 'received', 'pending']
        )
        for event in events_1day:
            sent_count += self._send_reminder(event, '1day')

        self.stdout.write(self.style.SUCCESS(f'Sent {sent_count} reminder(s)'))

    def _send_reminder(self, event, reminder_type):
        """Send a single reminder if not already sent."""
        # Check if already sent
        if EventReminder.objects.filter(event=event, reminder_type=reminder_type).exists():
            return 0

        admin_email = settings.ADMIN_ALERT_EMAIL
        days_text = '3 days' if reminder_type == '3day' else 'tomorrow'

        try:
            send_mail(
                subject=f'⏰ Event Reminder: {event.title} — {days_text}!',
                message=(
                    f'Hello,\n\n'
                    f'This is a reminder that the following event is {days_text}:\n\n'
                    f'📋 Event: {event.title}\n'
                    f'📅 Date: {event.date}\n'
                    f'📍 Venue: {event.venue}\n'
                    f'👥 Guests: {event.guests}\n'
                    f'📞 Contact: {event.contact_number or "N/A"}\n'
                    f'💰 Status: {event.status}\n\n'
                    f'Please ensure all preparations are on track.\n\n'
                    f'— Swagat Caterers System'
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[admin_email],
                fail_silently=True,
            )

            # Also send to assigned manager if exists
            if event.assigned_manager and event.assigned_manager.email:
                send_mail(
                    subject=f'⏰ Event Reminder: {event.title} — {days_text}!',
                    message=(
                        f'Hello {event.assigned_manager.first_name or "Manager"},\n\n'
                        f'Reminder: "{event.title}" is {days_text}.\n'
                        f'Venue: {event.venue} | Guests: {event.guests}\n\n'
                        f'Please ensure everything is ready.\n\n'
                        f'— Swagat Caterers'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[event.assigned_manager.email],
                    fail_silently=True,
                )

            # Record reminder
            EventReminder.objects.create(event=event, reminder_type=reminder_type)
            self.stdout.write(f'  ✅ {reminder_type} reminder sent for: {event.title}')
            return 1

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ❌ Failed for {event.title}: {e}'))
            return 0
