"""
URL configuration for backend_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backend_site/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from catering.views import frontend_home
from catering import views
from catering import exports as export_views
from django.contrib.auth import views as auth_views
from django.views.static import serve
from catering.views import activate_user

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', frontend_home, name='frontend_home'),
    path('api/manual-login/', views.manual_session_login, name='manual_login'),
    path('api/menu/activate/<str:token>/', activate_user, name='activate_user'),
    path('api/menu/', include('catering.urls')),
    path('', include('catering.urls')),
    # 2. The Authentication APIs (Login/Signup)
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),

    path('menu/', views.menu, name='menu'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact/', views.contact, name='contact'),
    path('book-now/', views.book_now, name='book_now'),
    path("custom-menu/", views.custom_menu, name="custom_menu"),
    path("home/", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("registration-pending/", views.registration_pending, name="registration_pending"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("profile/", views.profile, name="profile"),
    path("tracker/", views.tracker, name="tracker"),
    path("booking/", views.booking, name="booking"),
    path("direct-menu/", views.direct_menu, name="direct_menu"),
    path("create-menu/", views.create_menu, name="create_menu"),
    path("print-bill/", views.print_bill, name="print_bill"),

    path('dashboard/booking/', views.booking, name='booking'),

    # --- PLATFORM UPGRADE URLs ---
    path('booking/track/<uuid:token>/', views.booking_status, name='booking_status'),
    path('calendar/', views.calendar_public, name='calendar_public'),
    path('dashboard/gallery/', views.gallery_manage, name='gallery_manage'),
    path('my-tasks/', views.my_tasks_page, name='my_tasks_page'),
    path('activity-review/', views.activity_review_page, name='activity_review_page'),
    path('assign-tasks/', views.assign_tasks_page, name='assign_tasks_page'),
    path('view-menu/', views.view_menu_page, name='view_menu_page'),


    # Section 12: Exports
    path('export/events/excel/', export_views.export_events_excel, name='export_events_excel'),
    path('export/events/csv/', export_views.export_events_csv, name='export_events_csv'),
    path('export/members/excel/', export_views.export_members_excel, name='export_members_excel'),
    path('export/bookings/excel/', export_views.export_bookings_excel, name='export_bookings_excel'),
    
    # Export Preview Pages
    path('export/events/preview/', export_views.export_events_preview, name='export_events_preview'),
    path('export/bookings/preview/', export_views.export_bookings_preview, name='export_bookings_preview'),
    
    # Export Preview APIs (JSON)
    path('api/export/events/', export_views.export_events_api, name='export_events_api'),
    path('api/export/bookings/', export_views.export_bookings_api, name='export_bookings_api'),

    # Section 21: Blog
    path('blog/', include('blog.urls')),

    # Section 19: Login History Page
    path('login-history/', views.login_history_page, name='login_history_page'),

    # Section 23: Review System
    path('review/<uuid:token>/', views.review_page, name='review_page'),
    path('api/review/<uuid:token>/', views.submit_review, name='submit_review'),

    # Section 24: WhatsApp URL Generator (server-side emoji encoding)
    path('api/whatsapp/booking/<int:event_id>/', views.whatsapp_booking_url, name='whatsapp_booking_url'),
    path('api/whatsapp/review/<int:event_id>/', views.whatsapp_review_url, name='whatsapp_review_url'),

    # Section 25: Review Management (Admin)
    path('reviews/', views.admin_reviews_page, name='admin_reviews_page'),
    path('api/admin/reviews/', views.admin_reviews_list, name='admin_reviews_list'),
    path('api/admin/reviews/<int:review_id>/toggle-featured/', views.toggle_review_featured, name='toggle_review_featured'),
    path('api/admin/reviews/<int:review_id>/respond/', views.review_respond, name='review_respond'),
    path('api/admin/reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # Section 26: Sample Testimonials CRUD
    path('api/admin/samples/', views.sample_testimonials_list, name='sample_testimonials_list'),
    path('api/admin/samples/create/', views.sample_testimonial_create, name='sample_testimonial_create'),
    path('api/admin/samples/<int:sample_id>/update/', views.sample_testimonial_update, name='sample_testimonial_update'),
    path('api/admin/samples/<int:sample_id>/delete/', views.sample_testimonial_delete, name='sample_testimonial_delete'),
    
    # Section 27: Database Backup Trigger
    path('api/admin/backup/', views.trigger_backup, name='trigger_backup'),
    path('api/admin/backups/', views.list_backups, name='list_backups'),
    path('api/admin/backups/<str:filename>/download/', views.download_backup, name='download_backup'),
    path('api/admin/backups/<str:filename>/delete/', views.delete_backup, name='delete_backup'),

    path('api/', include('catering.urls')),
]
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
# This allows images to load
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers (work when DEBUG=False)
handler404 = 'catering.views.custom_404_view'