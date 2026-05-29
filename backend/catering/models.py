from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

# Custom UserManager to handle Djoser email-based registration
class CustomUserManager(UserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not username and email:
            # Auto-generate username from email if not provided
            username = email.split('@')[0]
            # Ensure uniqueness
            base_username = username
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
        return super().create_user(username=username, email=email, password=password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        if not username and email:
            username = email.split('@')[0]
        return super().create_superuser(username=username, email=email, password=password, **extra_fields)

# 1. CUSTOM USER MODEL
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default_user.png', blank=True)
    
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    objects = CustomUserManager()

    REQUIRED_FIELDS = ['email', 'phone_number']

    def __str__(self):
        return f"{self.username} ({self.user_type})"

# 2. CATEGORY MODEL
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    gujarati_name = models.CharField(max_length=100, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first (e.g. 1, 2, 3)")

    class Meta:
        ordering = ['order']  # This ensures API sends data in this order
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

# 3. MENU ITEM MODEL
class Menu_item(models.Model):
    category = models.ForeignKey(Category, related_name='items', on_delete=models.CASCADE)
    
    # Corrected 'Name' to 'name' (lowercase) for consistency
    name = models.CharField(max_length=100)
    # Added for Gujarati PDF Support
    gujarati_name = models.CharField(max_length=200, blank=True, null=True)
    
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='food_images/', blank=True, null=True)

    # Section 9: Tags for AI recommendation engine
    tags = models.CharField(max_length=500, blank=True, default='', help_text='Comma-separated tags e.g. wedding,starter,paneer')
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

# 4. MEMBER MODEL
class Member(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    default_rate = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

# 5. MEMBER LOG MODEL
class MemberLog(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    place = models.CharField(max_length=200)
    staff_count = models.IntegerField(default=0)
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_given = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    settled_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entry_by = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.name} - {self.date}"

# 6. CATERING EVENT MODEL
class CateringEvent(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, default="Not Specified") 
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    date = models.DateField()
    guests = models.IntegerField()
    event_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    event_city = models.CharField(max_length=100, blank=True, default='')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    
    # --- SECTION 3: Booking Tracking ---
    tracking_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='managed_events'
    )
    
    # --- NEW FIELDS FOR TRACKER & ANALYTICS ---
    rate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Rate per plate for this event")
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    staff_count = models.IntegerField(default=0, help_text="Number of staff assigned")
    
    # We keep this for backward compatibility
    menu_items = models.ManyToManyField(Menu_item, blank=True, related_name='events')

    # --- AUTOMATIC CALCULATIONS (No Database Migration needed for these properties) ---
    
    @property
    def total_cost(self):
        """Calculates Total Bill: Guests * Rate"""
        return self.guests * self.rate

    @property
    def pending_amount(self):
        """Calculates Pending: Total Cost - Advance"""
        return self.total_cost - self.advance_amount

    @property
    def is_settled(self):
        """Returns True if fully paid"""
        return self.pending_amount <= 0

    # --- SECTION 6: Internal Booking Notes ---
    internal_notes = models.TextField(blank=True, default='')
    notes_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='updated_notes'
    )
    notes_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_approved = models.BooleanField(default=True)  # False = pending admin review (manager-created)

    def __str__(self):
        return f"{self.title} ({self.date})"

# 7. NEW: MENU MODEL (For Multiple Menus per Event)
class Menu(models.Model):
    event = models.ForeignKey(CateringEvent, on_delete=models.CASCADE, related_name='menus')
    title = models.CharField(max_length=100) 
    price_per_plate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    items = models.ManyToManyField(Menu_item, blank=True)
    custom_items_text = models.TextField(blank=True, default='')  # JSON array of custom items [{name, categoryId}]
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
    created_by = models.CharField(max_length=100, blank=True, default='')
    is_approved = models.BooleanField(default=True)  # False = pending admin review

    def __str__(self):
        return f"{self.title} for {self.event.title}"
    
# 8. BOOKING MODEL
class Booking(models.Model):
    # Customer Details
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    # Event Details
    event_date = models.DateField()
    event_type = models.CharField(max_length=50)
    guest_count = models.IntegerField()
    meal_time = models.CharField(max_length=50, blank=True, null=True)
    package_type = models.CharField(max_length=100)
    
    # Venue & Message
    venue = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)

    # Timestamp (Auto-add when created)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.event_date}"


# =========================================
# NEW MODELS — PLATFORM UPGRADE
# =========================================

# 9. GALLERY ITEM MODEL (Section 2)
class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    CATEGORY_CHOICES = [
        ('wedding', 'Wedding'),
        ('corporate', 'Corporate'),
        ('birthday', 'Birthday'),
        ('food', 'Food'),
        ('setup', 'Setup'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES, default='image')
    cloudinary_url = models.URLField(max_length=500, blank=True, default='')
    youtube_url = models.URLField(max_length=500, blank=True, default='')
    image = models.FileField(upload_to='gallery/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='gallery_uploads'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Gallery Items'

    def __str__(self):
        return f"{self.title} ({self.media_type})"

    @property
    def media_url(self):
        """Returns the appropriate URL based on media type."""
        if self.cloudinary_url:
            return self.cloudinary_url
        if self.image:
            return self.image.url
        if self.youtube_url:
            return self.youtube_url
        return ''


# 10. MENU ITEM STATS (Section 10)
class MenuItemStats(models.Model):
    menu_item = models.OneToOneField(Menu_item, on_delete=models.CASCADE, related_name='stats')
    booking_count = models.IntegerField(default=0)
    profit_margin_pct = models.DecimalField(max_digits=5, decimal_places=2, default=30.00)
    seasonal_peak = models.CharField(
        max_length=50, blank=True, default='',
        help_text='Comma-separated month numbers, e.g. "11,12,1,2"'
    )

    class Meta:
        verbose_name_plural = 'Menu Item Stats'

    def __str__(self):
        return f"Stats: {self.menu_item.name} ({self.booking_count} bookings)"


# 11. ITEM CO-OCCURRENCE (Section 11)
class ItemCoOccurrence(models.Model):
    item_a = models.ForeignKey(Menu_item, on_delete=models.CASCADE, related_name='cooccurrence_a')
    item_b = models.ForeignKey(Menu_item, on_delete=models.CASCADE, related_name='cooccurrence_b')
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('item_a', 'item_b')
        verbose_name_plural = 'Item Co-Occurrences'

    def __str__(self):
        return f"{self.item_a.name} ↔ {self.item_b.name} ({self.count})"


# 12. EVENT STAFF (Section 13)
class EventStaff(models.Model):
    ROLE_CHOICES = [
        ('head_chef', 'Head Chef'),
        ('sous_chef', 'Sous Chef'),
        ('server', 'Server'),
        ('coordinator', 'Coordinator'),
        ('driver', 'Driver'),
    ]

    event = models.ForeignKey(CateringEvent, on_delete=models.CASCADE, related_name='staff_assignments')
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_assignments'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='server')
    confirmed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'member')
        verbose_name_plural = 'Event Staff'

    def __str__(self):
        return f"{self.member} → {self.event.title} ({self.role})"

    def clean(self):
        """Check for scheduling conflicts."""
        from django.core.exceptions import ValidationError
        conflicts = EventStaff.objects.filter(
            member=self.member,
            event__date=self.event.date
        ).exclude(pk=self.pk)
        if conflicts.exists():
            conflict_event = conflicts.first().event
            raise ValidationError(
                f"{self.member} is already assigned to '{conflict_event.title}' on {self.event.date}"
            )


# 13. ATTENDANCE (Section 13)
class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    event_staff = models.OneToOneField(EventStaff, on_delete=models.CASCADE, related_name='attendance')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    arrived_at = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    class Meta:
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.event_staff.member} - {self.status}"


# 14. EVENT REMINDER (Section 14)
class EventReminder(models.Model):
    REMINDER_CHOICES = [
        ('3day', '3 Days Before'),
        ('1day', '1 Day Before'),
    ]

    event = models.ForeignKey(CateringEvent, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=REMINDER_CHOICES)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'reminder_type')

    def __str__(self):
        return f"Reminder ({self.reminder_type}): {self.event.title}"


# 15. TASK ASSIGNMENT (Section 15)
class TaskAssignment(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks_assigned'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks_received'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    deadline = models.DateField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['deadline', '-priority']

    def __str__(self):
        return f"{self.title} → {self.assigned_to} ({self.status})"

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.deadline < timezone.now().date() and self.status != 'done'


# 16. USER LOGIN HISTORY (Section 17)
class UserLoginHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='login_history'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(default='')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_new_ip = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'User Login Histories'

    def __str__(self):
        return f"{self.user.username} from {self.ip_address} ({self.city})"

# 19. ACTIVITY LOGS (Manager Actions)
class ActivityLog(models.Model):
    RELATED_TYPES = [
        ('event', 'Event'),
        ('menu', 'Menu'),
        ('booking', 'Booking'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs'
    )
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    related_type = models.CharField(max_length=20, choices=RELATED_TYPES, default='other', blank=True)
    related_id = models.IntegerField(null=True, blank=True)
    related_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.action}"


# 17. ADMIN NOTES (visible only to admin)
class AdminNote(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_notes'
    )
    content = models.TextField()
    event = models.ForeignKey(
        'CateringEvent', null=True, blank=True, on_delete=models.CASCADE, related_name='admin_notes'
    )
    note_date = models.DateField(default=timezone.now)
    note_type = models.CharField(max_length=20, choices=[
        ('general', 'General'),
        ('event', 'Event Note'),
        ('tracker', 'Tracker Note'),
    ], default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-note_date', '-created_at']

    def __str__(self):
        return f"Note by {self.author.username} on {self.note_date}"

# Signal: Automatically create a Member object for Managers and Staff
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def user_post_save(sender, instance, created, **kwargs):
    # 1. Sync Staff/Manager to Tracker Members
    if instance.user_type in ['staff', 'manager']:
        Member.objects.get_or_create(
            name=instance.username,
            defaults={
                'phone': instance.phone_number or '',
                'default_rate': 0.00
            }
        )
    
    # 2. Send email to admin on new signup
    if created:
        from django.core.mail import send_mail
        import os
        admin_email = os.getenv('ADMIN_ALERT_EMAIL')
        if admin_email:
            subject = f"New User Signup: {instance.username}"
            message = f"A new user has registered.\n\nUsername: {instance.username}\nEmail: {instance.email}\nPhone: {instance.phone_number}\nRole: {instance.user_type}"
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email], fail_silently=True)
            except Exception as e:
                print(f"Failed to send signup email: {e}")

# 18. PDF GENERATION LOGS
class PdfLog(models.Model):
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    event_details = models.TextField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"PDF by {self.generated_by} on {self.generated_at}"