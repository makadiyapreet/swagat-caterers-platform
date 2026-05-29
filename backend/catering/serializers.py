from .models import Menu
from rest_framework import serializers
from .models import Menu_item , Category ,CateringEvent ,Member, MemberLog
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.core.signing import TimestampSigner
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import Category, Menu_item, CateringEvent, Member, MemberLog 
from .models import *

User = get_user_model()
signer = TimestampSigner()

# 1. Custom Registration Serializer
class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone_number')

    def create(self, validated_data):
        # Djoser overrides username with email when LOGIN_FIELD is 'email'.
        # We grab the original username from the raw request data and force it in.
        raw_username = self.initial_data.get('username', '').strip()
        if raw_username:
            validated_data['username'] = raw_username

        user = super().create(validated_data)

        # Double-check: ensure username is what the user typed, not auto-generated
        if raw_username and user.username != raw_username:
            user.username = raw_username

        # Lock account until admin approval
        user.is_active = False
        user.save()
        
        # Send email to admin with all signup details
        try:
            from django.utils import timezone
            now = timezone.now().strftime('%d/%m/%Y %I:%M %p')
            send_mail(
                subject=f'New Signup: {user.username} — Swagat Caterers',
                message=f"""
New User Registration
=====================
Username: {user.username}
Email: {user.email}
Phone: {user.phone_number or 'Not provided'}
Registered At: {now}

--- Action Required ---
Approve this user from the admin panel or use the link below:
/api/menu/activate/{signer.sign(user.pk)}/
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['swagatcaterersofficial@gmail.com'],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Signup email error: {e}")

        return user
# 2. Custom User Serializer for Dashboard View
class UserSerializer(BaseUserSerializer):

    profile_image = serializers.ImageField(read_only=True) # Read-only because updates go via request

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ('id', 'username', 'email', 'phone_number', 'user_type', 'is_staff', 'profile_image')

# 3. Menu Item Serializer
class MenuItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_item
        fields = ['id', 'Name', 'descp', 'image']

# 4. NEW: Category Serializer (Includes the items!)
class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'items']

# 5. Event Serializer
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CateringEvent
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu_item
        fields = '__all__'

class CateringEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CateringEvent
        fields = '__all__'

# --- NEW SERIALIZERS FOR TRACKER ---

class MemberLogSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    
    # Map frontend 'log_xxx' keys to model fields if needed, or stick to model fields
    log_date = serializers.DateField(source='date', read_only=True)
    log_place = serializers.CharField(source='place', read_only=True)
    log_staff = serializers.IntegerField(source='staff_count', read_only=True)
    log_rate = serializers.DecimalField(source='rate', max_digits=10, decimal_places=2, read_only=True)
    log_total = serializers.DecimalField(source='total_amount', max_digits=10, decimal_places=2, read_only=True)
    log_advance = serializers.DecimalField(source='advance_given', max_digits=10, decimal_places=2, read_only=True)
    log_settle = serializers.DecimalField(source='settled_amount', max_digits=10, decimal_places=2, read_only=True)
    log_entry_by = serializers.CharField(source='entry_by', read_only=True)

    class Meta:
        model = MemberLog
        fields = [
            'id', 'member_name', 'log_date', 'log_place', 'log_staff', 
            'log_rate', 'log_total', 'log_advance', 'log_settle', 
            'log_entry_by', 'advance_amount' # advance_amount comes from member relation usually
        ]
    
    # Custom field to get current balance in history if needed
    advance_amount = serializers.DecimalField(source='member.advance_amount', max_digits=10, decimal_places=2, read_only=True)


class MemberSerializer(serializers.ModelSerializer):
    # Write-only fields for updating the log simultaneously
    log_date = serializers.DateField(write_only=True, required=False)
    log_place = serializers.CharField(write_only=True, required=False)
    log_staff = serializers.IntegerField(write_only=True, required=False)
    log_rate = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    log_total = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    log_advance = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    log_settle = serializers.DecimalField(write_only=True, max_digits=10, decimal_places=2, required=False)
    log_entry_by = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Member
        fields = '__all__'

    def update(self, instance, validated_data):
        # Extract log data
        log_data = {
            'date': validated_data.pop('log_date', None),
            'place': validated_data.pop('log_place', None),
            'staff_count': validated_data.pop('log_staff', 0),
            'rate': validated_data.pop('log_rate', 0),
            'total_amount': validated_data.pop('log_total', 0),
            'advance_given': validated_data.pop('log_advance', 0),
            'settled_amount': validated_data.pop('log_settle', 0),
            'entry_by': validated_data.pop('log_entry_by', '')
        }

        # Update Member
        instance = super().update(instance, validated_data)

        # Create Log if data exists
        if log_data['date'] and log_data['place']:
            MemberLog.objects.create(member=instance, **log_data)

        return instance
    
class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class CateringEventSerializer(serializers.ModelSerializer):
    # This will fetch all menus associated with the event automatically
    menus = MenuSerializer(many=True, read_only=True)

    class Meta:
        model = CateringEvent
        fields = '__all__'