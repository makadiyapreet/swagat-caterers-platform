import os
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.utils.html import strip_tags

User = get_user_model()
signer = Signer()

SITE_DOMAIN = os.environ.get('SITE_URL', 'https://swagatcaterers.in')

@receiver(post_save, sender=User)
def deactivate_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # Deactivate User immediately (admin email is sent from the serializer)
        User.objects.filter(pk=instance.pk).update(is_active=False)
        print(f"✅ New user '{instance.username}' deactivated, pending admin approval.")



# 2. ADMIN APPROVES -> SEND WELCOME EMAIL TO USER
@receiver(pre_save, sender=User)
def check_active_status(sender, instance, **kwargs):
    if instance.pk: 
        try:
            old_user = User.objects.get(pk=instance.pk)
            
            # If Admin changes "Inactive" -> "Active"
            if not old_user.is_active and instance.is_active:
                print(f"User {instance.username} activated. Preparing Welcome Email...")

                subject = '🎉 Welcome to Swagat Caterers! Your Account is Approved'
                
                # NOTE: We use SITE_DOMAIN here (defined at the top)
                html_message = f"""
                <html>
                <body>
                    <h2>Hello {instance.username},</h2>
                    <p>Your account has been approved!</p>
                    <a href="{SITE_DOMAIN}/login/">Login to Dashboard</a>
                </body>
                </html>
                """
                
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message, 
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[instance.email],
                    html_message=html_message,
                    fail_silently=True,
                )
                print(f"✅ Welcome Email Sent to {instance.email}")

        except Exception as e:
             # THIS PREVENTS THE 500 ERROR
            print(f"❌ ERROR in check_active_status: {str(e)}")


# =========================================
# SECTION 17: Suspicious Login Detection
# =========================================
from django.contrib.auth.signals import user_logged_in
import requests as http_requests


@receiver(user_logged_in)
def track_user_login(sender, request, user, **kwargs):
    """Track login IP addresses and detect new/suspicious logins."""
    from .models import UserLoginHistory

    try:
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '127.0.0.1')

        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # Check if this IP has been used before
        is_new_ip = not UserLoginHistory.objects.filter(
            user=user, ip_address=ip
        ).exists()

        # Get location from ip-api (free, no key needed)
        city = ''
        country = ''
        try:
            if ip not in ('127.0.0.1', 'localhost', '::1', '13.207.76.139'):
                geo_resp = http_requests.get(
                    f'http://ip-api.com/json/{ip}?fields=city,country',
                    timeout=3
                )
                if geo_resp.status_code == 200:
                    geo_data = geo_resp.json()
                    city = geo_data.get('city', '')
                    country = geo_data.get('country', '')
        except Exception:
            pass

        # Record login
        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip,
            user_agent=user_agent,
            is_new_ip=is_new_ip,
            city=city,
            country=country,
        )

        # Login recorded — no email notification sent.
        # Email notifications are only sent for task assignments.

    except Exception as e:
        print(f"❌ Login tracking error: {e}")