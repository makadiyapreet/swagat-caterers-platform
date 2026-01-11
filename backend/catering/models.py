from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. CUSTOM USER MODEL
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png', blank=True)
    
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('manager', 'Manager'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')

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
# 6. CATERING EVENT MODEL
class CateringEvent(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    venue = models.CharField(max_length=200, default="Not Specified") 
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    
    date = models.DateField()
    guests = models.IntegerField()
    event_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
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

    def __str__(self):
        return f"{self.title} ({self.date})"

# 7. NEW: MENU MODEL (For Multiple Menus per Event)
class Menu(models.Model):
    event = models.ForeignKey(CateringEvent, on_delete=models.CASCADE, related_name='menus')
    title = models.CharField(max_length=100) 
    price_per_plate = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # e.g., "Lunch", "Dinner", "Kids Menu"
    items = models.ManyToManyField(Menu_item, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

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