from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.html import strip_tags
from django.core.signing import Signer

User = get_user_model()
signer = Signer()

# --- CONFIGURATION ---
# CHANGE THIS to your actual live website URL
# (Do not add a trailing slash at the end)
SITE_DOMAIN = "https://swagat-caterers-platform-production.up.railway.app" 


# 1. NEW USER REGISTRATION -> DEACTIVATE & EMAIL ADMIN
@receiver(post_save, sender=User)
def deactivate_new_user(sender, instance, created, **kwargs):
    # Check if this is a new user and NOT a superuser
    if created and not instance.is_superuser:
        
        # A. Set user to inactive immediately so they can't login
        instance.is_active = False 
        instance.save()
        
        # B. Generate the Magic Link for the Admin
        # We sign the User ID so the link is secure
        token = signer.sign(instance.pk)
        
        # This link goes to your backend view that activates the user
        activation_link = f"{SITE_DOMAIN}/api/menu/activate/{token}/"
        
        # C. Email the ADMIN
        print(f"New user registered: {instance.username}. Sending approval email to Admin...")
        
        send_mail(
            subject=f'⚠️ APPROVAL NEEDED: New User "{instance.username}"',
            message=f"""
            A new user has just registered.
            
            -----------------------------------------
            USER DETAILS
            -----------------------------------------
            Username: {instance.username}
            Email:    {instance.email}
            
            -----------------------------------------
            ACTION REQUIRED
            -----------------------------------------
            Click the link below to approve this user immediately:
            
            {activation_link}
            
            (Clicking this will activate their account and automatically send them a welcome email.)
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['swagatcaterersofficial@gmail.com'], # The Admin's email
            fail_silently=False,
        )


# 2. ADMIN APPROVES -> SEND WELCOME EMAIL TO USER
@receiver(pre_save, sender=User)
def check_active_status(sender, instance, **kwargs):
    if instance.pk: # Ensure this isn't a new user being created for the first time
        try:
            # Fetch the old version of this user from the DB
            old_user = User.objects.get(pk=instance.pk)
            
            # Check if Admin just changed "Inactive" -> "Active"
            if not old_user.is_active and instance.is_active:
                print(f"User {instance.username} has been activated. Sending welcome email...")

                # 1. Define the Subject
                subject = '🎉 Welcome to Swagat Caterers! Your Account is Approved'
                
                # 2. Define the HTML Message (Beautiful Version)
                html_message = f"""
                <html>
                <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-top: 5px solid #D4AF37; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        
                        <h2 style="color: #D4AF37; text-align: center; margin-top: 0;">Hello {instance.username},</h2>
                        
                        <p style="font-size: 16px;">We’re excited to share some great news! 🎉</p>
                        
                        <p style="font-size: 16px;">Your account has been successfully approved by our admin team.</p>
                        
                        <p style="font-size: 16px;">You can now access your dashboard and start exploring all the features by clicking the button below:</p>
                        
                        <div style="text-align: center; margin: 35px 0;">
                            <a href="{SITE_DOMAIN}/login/" 
                            style="background-color: #D4AF37; color: white; padding: 14px 30px; text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px; display: inline-block; transition: background 0.3s;">
                            Login to Dashboard
                            </a>
                        </div>
                        
                        <p style="font-size: 14px; color: #555;">If you need any assistance, feel free to reach out — we’re always happy to help.</p>
                        
                        <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                        
                        <p style="text-align: center; color: #888; font-size: 12px;">
                            <b>Swagat Caterers Team</b><br>
                            🍽️ <i>Serving with Taste & Trust.</i>
                        </p>
                    </div>
                </body>
                </html>
                """
                
                # 3. Define Plain Text Fallback
                plain_message = strip_tags(html_message)
                
                # 4. Send the Email to the USER
                send_mail(
                    subject=subject,
                    message=plain_message, 
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[instance.email], # Sends to the User
                    html_message=html_message,
                    fail_silently=False,
                )
        except User.DoesNotExist:
            pass