"""
Section 20: Permission Template Tags
Usage in templates:
    {% load permissions %}
    {% has_permission user 'can_view_billing' as can_bill %}
    {% if can_bill %}...{% endif %}
"""
from django import template
from catering.decorators import has_permission, get_user_permissions

register = template.Library()


@register.simple_tag
def has_perm(user, permission_name):
    """Check if user has a specific permission. Returns True/False."""
    return has_permission(user, permission_name)


@register.simple_tag
def user_role(user):
    """Get user's role display name."""
    if not user.is_authenticated:
        return 'anonymous'
    return getattr(user, 'user_type', 'customer')


@register.filter
def is_role(user, role_name):
    """Template filter to check role. Usage: {% if user|is_role:'admin' %}"""
    if not user.is_authenticated:
        return False
    return getattr(user, 'user_type', 'customer') == role_name


@register.filter
def is_internal(user):
    """Check if user is any internal role (not customer)."""
    if not user.is_authenticated:
        return False
    return getattr(user, 'user_type', 'customer') != 'customer'
