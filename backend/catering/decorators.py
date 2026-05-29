"""
Role-based access control decorators for Swagat Caterers.
Usage: @require_role(['admin', 'manager'])
"""
from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required


# Permission matrix: role -> set of permissions
ROLE_PERMISSIONS = {
    'admin': {
        'can_view_dashboard', 'can_manage_events', 'can_manage_bookings',
        'can_manage_menu', 'can_manage_categories', 'can_manage_gallery',
        'can_manage_staff', 'can_manage_members', 'can_view_billing',
        'can_export_data', 'can_manage_users', 'can_assign_tasks',
        'can_view_reports', 'can_manage_blog', 'can_view_analytics',
        'can_update_event_status', 'can_view_internal_notes',
        'can_schedule_staff', 'can_view_login_history',
    },
    'manager': {
        'can_view_dashboard', 'can_manage_events', 'can_manage_bookings',
        'can_manage_menu', 'can_manage_categories', 'can_manage_gallery',
        'can_manage_staff', 'can_view_billing', 'can_export_data',
        'can_view_reports', 'can_view_analytics',
        'can_update_event_status', 'can_view_internal_notes',
        'can_schedule_staff', 'can_assign_tasks',
    },
    'event_manager': {
        'can_view_dashboard', 'can_manage_events', 'can_manage_bookings',
        'can_schedule_staff', 'can_update_event_status',
        'can_view_internal_notes',
    },
    'kitchen_manager': {
        'can_view_dashboard', 'can_manage_menu', 'can_manage_categories',
    },
    'accountant': {
        'can_view_dashboard', 'can_view_billing', 'can_export_data',
        'can_view_reports',
    },
    'staff': {
        'can_view_dashboard',
    },
    'customer': set(),
}


def get_user_permissions(user):
    """Get the full set of permissions for a user based on their role."""
    if not user.is_authenticated:
        return set()
    user_type = getattr(user, 'user_type', 'customer')
    return ROLE_PERMISSIONS.get(user_type, set())


def has_permission(user, permission):
    """Check if a user has a specific permission."""
    return permission in get_user_permissions(user)


def require_role(allowed_roles):
    """
    Decorator that restricts view access to specific user roles.
    Usage:
        @require_role(['admin', 'manager'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            user_type = getattr(request.user, 'user_type', 'customer')
            if user_type in allowed_roles:
                return view_func(request, *args, **kwargs)

            # Check if it's an API request
            if request.headers.get('Content-Type') == 'application/json' or \
               request.path.startswith('/api/'):
                return JsonResponse(
                    {'error': 'Insufficient permissions', 'required_roles': allowed_roles},
                    status=403
                )

            return HttpResponseForbidden(
                '<div style="text-align:center; padding:50px; font-family:sans-serif;">'
                '<h1 style="color:#D4AF37;">Access Denied</h1>'
                '<p>You do not have permission to access this page.</p>'
                f'<p>Required role: {", ".join(allowed_roles)}</p>'
                '<a href="/dashboard/" style="color:#D4AF37;">← Back to Dashboard</a>'
                '</div>'
            )
        return wrapper
    return decorator


def require_permission(permission_name):
    """
    Decorator that restricts view access based on specific permission.
    Usage:
        @require_permission('can_view_billing')
        def billing_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if has_permission(request.user, permission_name):
                return view_func(request, *args, **kwargs)

            if request.headers.get('Content-Type') == 'application/json' or \
               request.path.startswith('/api/'):
                return JsonResponse(
                    {'error': f'Missing permission: {permission_name}'},
                    status=403
                )

            return HttpResponseForbidden(
                '<div style="text-align:center; padding:50px; font-family:sans-serif;">'
                '<h1 style="color:#D4AF37;">Access Denied</h1>'
                f'<p>Missing permission: {permission_name}</p>'
                '<a href="/dashboard/" style="color:#D4AF37;">← Back to Dashboard</a>'
                '</div>'
            )
        return wrapper
    return decorator
