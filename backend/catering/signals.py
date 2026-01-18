from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.signing import Signer
from django.utils.html import strip_tags

User = get_user_model()
signer = Signer()

SITE_DOMAIN = "https://swagat-caterers-platform-production.up.railway.app"

@receiver(post_save, sender=User)
def deactivate_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        # 1. Deactivate User
        User.objects.filter(pk=instance.pk).update(is_active=False)
        
        # 2. Try to Send Email (But don't crash if it fails)
        try:
            print(f"Attempting to email Admin for user: {instance.username}")
            
            token = signer.sign(instance.pk)
            activation_link = f"{SITE_DOMAIN}/api/menu/activate/{token}/"
            
            send_mail(
                subject=f'APPROVAL NEEDED: {instance.username}',
                message=f"Approve here: {activation_link}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['swagatcaterersofficial@gmail.com'],
                fail_silently=False,
            )
            print("✅ Email Sent Successfully!")
            
        except Exception as e:
            # This prints the REAL error to your logs but lets the user signup finish!
            print(f"❌ EMAIL FAILED: {str(e)}")


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
                    fail_silently=False,
                )
                print(f"✅ Welcome Email Sent to {instance.email}")

        except Exception as e:
             # THIS PREVENTS THE 500 ERROR
            print(f"❌ ERROR in check_active_status: {str(e)}")