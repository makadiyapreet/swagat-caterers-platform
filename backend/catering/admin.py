from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Menu_item, Member, MemberLog, CateringEvent, Menu , Booking
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Menu_item, Member, MemberLog, CateringEvent, Menu, Booking

class MyUserAdmin(UserAdmin):
    model = User
    # This shows your custom fields in the list view
    list_display = ['username', 'email', 'phone_number', 'user_type', 'is_staff']
    
    # This adds your custom fields to the edit screens
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'user_type', 'profile_image')}),
    )
    # This adds your custom fields to the "Add User" screen
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('phone_number', 'user_type', 'email')}),
    )

# Replace your current register line with this:
admin.site.register(User, MyUserAdmin)

# 2. Inline for Menu Items (Edit items inside Category)
class MenuItemInline(admin.TabularInline):
    model = Menu_item
    extra = 1

# 3. Category Admin (With Sorting & Inline)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [MenuItemInline]
    # 'order' allows you to type 1, 2, 3 to sort categories
    list_display = ['name', 'gujarati_name', 'order'] 
    list_editable = ['order'] 
    ordering = ['order'] 

# 4. Menu Item Admin
@admin.register(Menu_item)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'gujarati_name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'gujarati_name']

# 5. Register Other Models
admin.site.register(Member)
admin.site.register(MemberLog)
admin.site.register(CateringEvent)
admin.site.register(Menu)

# 6. Catering Event Admin
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'event_date', 'event_type', 'created_at')
    list_filter = ('event_type', 'event_date')
    search_fields = ('name', 'phone')