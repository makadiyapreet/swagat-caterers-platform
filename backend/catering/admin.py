from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Category, Menu_item, Member, MemberLog, CateringEvent, Menu, Booking,
    GalleryItem, MenuItemStats, ItemCoOccurrence, EventStaff, Attendance,
    EventReminder, TaskAssignment, UserLoginHistory
)

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


# =========================================
# NEW MODEL ADMINS — PLATFORM UPGRADE
# =========================================

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'media_type', 'created_at', 'uploaded_by')
    list_filter = ('category', 'media_type')
    search_fields = ('title',)

@admin.register(MenuItemStats)
class MenuItemStatsAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'booking_count', 'profit_margin_pct')
    ordering = ('-booking_count',)

@admin.register(ItemCoOccurrence)
class ItemCoOccurrenceAdmin(admin.ModelAdmin):
    list_display = ('item_a', 'item_b', 'count')
    ordering = ('-count',)

@admin.register(EventStaff)
class EventStaffAdmin(admin.ModelAdmin):
    list_display = ('event', 'member', 'role', 'confirmed')
    list_filter = ('role', 'confirmed')
    list_editable = ('confirmed',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('event_staff', 'status', 'arrived_at')
    list_filter = ('status',)

@admin.register(EventReminder)
class EventReminderAdmin(admin.ModelAdmin):
    list_display = ('event', 'reminder_type', 'sent_at')
    list_filter = ('reminder_type',)

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'assigned_by', 'deadline', 'priority', 'status')
    list_filter = ('status', 'priority')
    search_fields = ('title',)
    list_editable = ('status',)

@admin.register(UserLoginHistory)
class UserLoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'city', 'country', 'is_new_ip', 'timestamp')
    list_filter = ('is_new_ip',)
    search_fields = ('user__username', 'ip_address')