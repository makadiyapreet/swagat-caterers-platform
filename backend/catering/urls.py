from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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
    path('send-email/', views.send_enquiry_email, name='send_enquiry_email'),

    # 2. General APIs
    path('menu-list/', views.get_menu, name='menu-list'),  # Public Menu
    path('activate/<str:token>/', views.activate_user, name='activate-user'), # User Activation
    path('update-profile/', views.update_profile, name='update-profile'), # Profile Update

]