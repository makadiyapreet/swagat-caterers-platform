import os
import django
from django.conf import settings

# 1. Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_site.settings')
django.setup()

print("--- DJANGO PATH DIAGNOSTICS ---")
print(f"BASE_DIR:   {settings.BASE_DIR}")
print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"MEDIA_URL:  {settings.MEDIA_URL}")
print(f"DEBUG Mode: {settings.DEBUG}")

# 2. Check if the physical folder exists
if os.path.exists(settings.MEDIA_ROOT):
    print("\n✅ SUCCESS: The MEDIA_ROOT folder exists on your disk.")
    
    # Check for the subfolder
    subfolder = os.path.join(settings.MEDIA_ROOT, 'profile_images')
    if os.path.exists(subfolder):
        print(f"✅ SUCCESS: Subfolder 'profile_images' found.")
        
        # Check for specific files
        files = os.listdir(subfolder)
        print(f"📁 Files found in profile_images: {files}")
    else:
        print("❌ ERROR: 'profile_images' subfolder NOT found inside media.")
else:
    print("\n❌ ERROR: The MEDIA_ROOT folder does NOT exist at the path above.")

print("\n--- END OF DIAGNOSTICS ---")