"""
Context processor that injects user permissions into every template context.
Add 'catering.context_processors.user_permissions' to TEMPLATES settings.
"""
from .decorators import get_user_permissions, ROLE_PERMISSIONS


def user_permissions(request):
    """
    Injects user permission flags into template context.
    Usage in templates: {% if user_permissions.can_view_billing %}
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {'user_permissions': {}, 'user_role': 'anonymous'}

    user = request.user
    user_type = getattr(user, 'user_type', 'customer')
    perms = get_user_permissions(user)

    # Convert set to dict for easier template access
    all_possible_perms = set()
    for role_perms in ROLE_PERMISSIONS.values():
        all_possible_perms.update(role_perms)

    perm_dict = {perm: (perm in perms) for perm in all_possible_perms}

    return {
        'user_permissions': perm_dict,
        'user_role': user_type,
        'is_admin_user': user_type == 'admin',
        'is_manager_user': user_type in ('admin', 'manager'),
        'is_staff_user': user_type in ('admin', 'manager', 'staff', 'event_manager', 'kitchen_manager', 'accountant'),
    }
