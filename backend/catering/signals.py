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
        # 1. Deactivate User immediately
        User.objects.filter(pk=instance.pk).update(is_active=False)
        
        # 2. Prepare Email Details
        try:
            print(f"Attempting to email Admin for user: {instance.username}")
            
            token = signer.sign(instance.pk)
            activation_link = f"{SITE_DOMAIN}/api/menu/activate/{token}/"
            
            # --- NEW: Gather User Details ---
            user_details = f"""
            <table style="border-collapse: collapse; width: 100%; max_width: 600px;">
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Username:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{instance.username}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Email:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{instance.email}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>First Name:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{getattr(instance, 'first_name', '-')}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Last Name:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{getattr(instance, 'last_name', '-')}</td></tr>
                <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Date Joined:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{instance.date_joined.strftime('%Y-%m-%d %H:%M')}</td></tr>
            </table>
            """

            # --- NEW: HTML Email Message ---
            html_message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #D4AF37;">New Registration Request</h2>
                <p>A new user has signed up and is waiting for approval.</p>
                
                <h3>User Details:</h3>
                {user_details}
                
                <br>
                <div style="text-align: center; margin: 20px 0;">
                    <a href="{activation_link}" style="background-color: #D4AF37; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                        Review & Approve User
                    </a>
                </div>
                
                <p style="font-size: 12px; color: #888;">If the button above doesn't work, copy this link:<br>{activation_link}</p>
            </body>
            </html>
            """
            
            # Create a plain text version for email clients that don't support HTML
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=f'🔔 APPROVAL NEEDED: {instance.username}',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['swagatcaterersofficial@gmail.com'], # <--- Your Admin Email
                html_message=html_message, # <--- Attach the HTML version
                fail_silently=False,
            )
            print("✅ Admin Notification Email Sent Successfully!")
            
        except Exception as e:
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