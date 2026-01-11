from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from django.core.signing import Signer # Import this

signer = Signer()


@receiver(post_save, sender=User)
def deactivate_new_user(sender, instance, created, **kwargs):
    if created and not instance.is_superuser:
        instance.is_active = False 
        instance.save()
        
        # 1. Generate the Magic Link
        # We sign the User ID so no one can fake it
        token = signer.sign(instance.pk)
        
        # NOTE: When you deploy, change 127.0.0.1 to your real website domain
        activation_link = f"http://127.0.0.1:8000/api/menu/activate/{token}/"
        
        # 2. Email You with the Link
        send_mail(
            subject=f'APPROVAL NEEDED: New User "{instance.username}"',
            message=f"""
            A new user has registered.
            
            Username: {instance.username}
            Email: {instance.email}
            
            -----------------------------------------
            CLICK BELOW TO APPROVE IMMEDIATELY:
            {activation_link}
            -----------------------------------------
            
            (Clicking this will activate the account and email the user automatically.)
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['swagatcaterersofficial@gmail.com'],
            fail_silently=False,
        )

# 2. ADMIN APPROVES -> Email THE USER
User = get_user_model()

# We ONLY handle the "Account Approved" email here now
@receiver(pre_save, sender=User)
def check_active_status(sender, instance, **kwargs):
    if instance.pk: # Ensure user exists
        try:
            old_user = User.objects.get(pk=instance.pk)
            
            # If Admin changes "Inactive" -> "Active"
            if not old_user.is_active and instance.is_active:
                print(f"User {instance.username} approved. Sending welcome email...")
                
                # 1. Define the Subject
                subject = '🎉 Welcome to Swagat Caterers! Your Account is Approved'
                
                # 2. Define the HTML Message (The beautiful version)
                html_message = f"""
                <html>
                <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                        
                        <h2 style="color: #D4AF37; text-align: center;">Hello {instance.username},</h2>
                        
                        <p>We’re excited to share some great news! 🎉</p>
                        
                        <p>Your account has been successfully approved by our admin team.</p>
                        
                        <p>You can now access your dashboard and start exploring all the features by clicking the link below:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ site_url }}/login.html" 
                               style="background-color: #D4AF37; color: white; padding: 12px 25px; text-decoration: none; font-weight: bold; border-radius: 4px; display: inline-block;">
                               Login to your Dashboard
                            </a>
                        </div>
                        
                        <p>If you need any assistance or have questions while getting started, feel free to reach out — we’re always happy to help.</p>
                        
                        <p>Thank you for choosing Swagat Caterers. We look forward to serving you!</p>
                        
                        <br>
                        <p style="color: #666;">
                            Warm regards,<br>
                            <b>Swagat Caterers Team</b><br>
                            🍽️ <i>Serving with Taste & Trust.</i>
                        </p>
                    </div>
                </body>
                </html>
                """
                
                # 3. Define Plain Text Fallback (For email clients that block HTML)
                plain_message = strip_tags(html_message)
                
                # 4. Send the Email
                send_mail(
                    subject=subject,
                    message=plain_message, # Fallback text
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[instance.email],
                    html_message=html_message, # This makes it look good!
                    fail_silently=False,
                )
        except User.DoesNotExist:
            pass