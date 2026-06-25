from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import chatbot as chatbot_views

# Create a router and register our ViewSets with it.
router = DefaultRouter()

# --- Standard Menu & Events ---
router.register(r'categories', views.CategoryViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'events', views.EventViewSet)
router.register(r'menus', views.MenuViewSet)

# --- Tracker & Reports ---
router.register(r'members', views.MemberViewSet)
router.register(r'logs', views.MemberLogViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # 1. Router URLs (Handles: /members/, /logs/, /events/, /categories/, /menu-items/)
    path('', include(router.urls)),

    path('api/book-event/', views.book_event_api, name='book_event_api'),
    path('api/log-pdf/', views.log_pdf_download, name='log_pdf_download'),
    path('send-email/', views.send_enquiry_email, name='send_enquiry_email'),

    # 2. General APIs
    path('menu-list/', views.get_menu, name='menu-list'),  # Public Menu
    path('activate/<str:token>/', views.activate_user, name='activate-user'), # User Activation
    path('update-profile/', views.update_profile, name='update-profile'), # Profile Update

    # --- PLATFORM UPGRADE URLs ---
    # Section 2: Gallery
    path('api/gallery/', views.gallery_api, name='gallery_api'),
    path('api/gallery/upload/', views.gallery_upload, name='gallery_upload'),
    path('api/gallery/<int:item_id>/delete/', views.gallery_delete, name='gallery_delete'),

    # Section 4: Calendar
    path('api/events/calendar/', views.calendar_api, name='calendar_api'),

    # Section 5: Weather Suggestions
    path('api/weather-suggest/', views.weather_suggest, name='weather_suggest'),

    # Section 6: Internal Notes
    path('api/events/<int:event_id>/notes/', views.save_internal_notes, name='save_internal_notes'),

    # Section 3: Event Status Update
    path('api/events/<int:event_id>/status/', views.update_event_status, name='update_event_status'),

    # Section 13: Staff Scheduling
    path('api/events/<int:event_id>/staff/', views.event_staff_api, name='event_staff_api'),

    # Section 15: Tasks
    path('api/tasks/', views.task_api, name='task_api'),
    path('api/tasks/<int:task_id>/status/', views.task_update_status, name='task_update_status'),

    # Section 17: Admin Notes
    path('api/admin-notes/', views.admin_notes_api, name='admin_notes_api'),
    path('api/admin-notes/<int:note_id>/delete/', views.admin_note_delete, name='admin_note_delete'),
    path('api/admin-notes/download/', views.admin_notes_download, name='admin_notes_download'),

    # Section 17b: Staff/Manager Users list
    path('api/staff-users/', views.staff_users_api, name='staff_users_api'),
    path('api/admin/delete-user/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    
    # Section 18: Activity Logs (Manager Actions)
    path('api/activity-logs/', views.activity_logs_api, name='activity_logs_api'),

    # Section 4: Public APIs (for calendar/recommendations)
    path('api/menu/items/', views.menu_items_public, name='menu_items_public'),
    path('api/events/list/', views.events_list_public, name='events_list_public'),

    # Section 7: Public Chatbot
    path('chatbot/', chatbot_views.public_chatbot, name='public_chatbot'),

    # Section 8: Admin Chatbot
    path('admin-chat/', chatbot_views.admin_chatbot, name='admin_chatbot'),

    # Section 9: Menu Recommendations
    path('api/menu/recommend/', views.menu_recommend, name='menu_recommend'),

    # Section 11: Co-occurrence (Also Selected)
    path('api/menu/also-selected/<int:item_id>/', views.also_selected_api, name='also_selected_api'),

    # Section 19: Login History
    path('api/login-history/', views.login_history_api, name='login_history_api'),
    path('api/logout-all/', views.logout_all_sessions, name='logout_all_sessions'),
]