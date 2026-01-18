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
from django.contrib.auth import views as auth_views
from django.views.static import serve
from catering.views import activate_user # <-- USE THIS

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', frontend_home, name='frontend_home'),
    path('api/manual-login/', views.manual_session_login, name='manual_login'),
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
    path("index/", views.index, name="index"),
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


    path('api/', include('catering.urls'))
]
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    path('api/menu/activate/<str:token>/', activate_user, name='activate_user'),
    ]
# This allows images to load
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)