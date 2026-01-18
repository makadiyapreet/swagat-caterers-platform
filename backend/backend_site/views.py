from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.signing import Signer, BadSignature

User = get_user_model()
signer = Signer()

def activate_user(request, token):
    """
    This view is clicked by YOU (The Admin).
    It verifies the digital signature and activates the user.
    """
    try:
        # 1. Unsign the token to get the User ID
        # max_age=86400 means the link is valid for 24 hours
        user_id = signer.unsign(token, max_age=86400)
        
        # 2. Get the user from the DB
        user = User.objects.get(pk=user_id)
        
        # 3. Activate the user
        if not user.is_active:
            user.is_active = True
            user.save() # This triggers the 'pre_save' signal to email the user!
            
            return HttpResponse(f"""
                <div style='font-family: sans-serif; text-align: center; padding: 50px;'>
                    <h1 style='color: green;'>✅ Approved!</h1>
                    <p>User <b>{user.username}</b> ({user.email}) has been activated.</p>
                    <p>A welcome email has been sent to them automatically.</p>
                </div>
            """)
        else:
            return HttpResponse(f"""
                <div style='font-family: sans-serif; text-align: center; padding: 50px;'>
                    <h1 style='color: orange;'>⚠️ Already Active</h1>
                    <p>User <b>{user.username}</b> is already approved.</p>
                </div>
            """)
            
    except BadSignature:
        return HttpResponse("<h1>❌ Error: Invalid or Expired Link</h1>", status=400)
    except User.DoesNotExist:
        return HttpResponse("<h1>❌ Error: User not found</h1>", status=404)