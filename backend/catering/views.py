from multiprocessing.managers import Token
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from .models import *
from .serializers import *
from django.http import JsonResponse
from django.core.mail import send_mail
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def custom_404_view(request, exception):
    """Custom 404 error page."""
    return render(request, '404.html', status=404)

# --- IMPORTS ---
from .models import Category, Menu_item, CateringEvent, Member, MemberLog , Menu, Booking
from .serializers import (
    CategorySerializer, 
    MenuItemSerializer, 
    CateringEventSerializer, 
    MemberSerializer, 
    MemberLogSerializer
)
from django.contrib.auth import login
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import permissions
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.core.signing import Signer, BadSignature

domin = "https://swagatcaterers.in"
User = get_user_model()
signer = Signer()

@csrf_exempt
def activate_user(request, token):
    try:
        # 1. Decode the secure token to get the User ID
        user_id = signer.unsign(token)
        
        # 2. Get the user
        user = get_object_or_404(User, pk=user_id)
        
        # 3. Handle the 'Approve' Button Click (POST request)
        if request.method == 'POST':
            selected_role = request.POST.get('role')
            user.user_type = selected_role
            user.is_active = True
            
            # Auto-promote Managers/Admins/Staff to staff so they can log in
            if selected_role in ['manager', 'admin', 'staff']:
                user.is_staff = True
                
            user.save() 
            return HttpResponse(f"<h1 style='color:green; text-align:center;'>Success! User {user.username} is active.</h1>")

        # 4. Show the Approval Page (GET request)
        return HttpResponse(f"""
            <html>
            <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                <h2>Approve User: {user.username}</h2>
                <p>Email: {user.email}</p>
                <form method="POST">
                    <label>Assign Role:</label>
                    <select name="role" style="padding:10px; margin:10px; font-size:16px;">
                        <option value="customer">Customer</option>
                        <option value="staff">Staff</option>
                        <option value="manager">Manager</option>
                        <option value="admin">Admin</option>
                    </select>
                    <br><br>
                    <button type="submit" style="padding:10px 20px; background:#D4AF37; color:white; border:none; cursor:pointer; font-size:16px;">
                        Approve User
                    </button>
                </form>
            </body>
            </html>
        """)
            
    except BadSignature:
        return HttpResponse("<h1 style='color:red; text-align:center;'>Invalid or Expired Link</h1>", status=400)
    except Exception as e:
        # This will catch any other errors and print them clearly
        return HttpResponse(f"<h1 style='color:red; text-align:center;'>Server Error: {str(e)}</h1>", status=500)

# --- 2. MENU API ---
@api_view(['GET'])
def get_menu(request):
    categories = Category.objects.prefetch_related('items').all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# --- 3. PROFILE UPDATE VIEW ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    if 'email' in request.data: user.email = request.data['email']
    if 'phone' in request.data: user.phone_number = request.data['phone']
    if 'profile_image' in request.FILES: user.profile_image = request.FILES['profile_image']
    user.save()
    return Response({'status': 'success', 'message': 'Profile updated!'})

# --- 4. VIEWSETS (CRUD) ---

# *** THIS WAS MISSING PREVIOUSLY ***
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = Menu_item.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

class EventViewSet(viewsets.ModelViewSet):
    queryset = CateringEvent.objects.all()
    serializer_class = CateringEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_type = getattr(user, 'user_type', 'customer')
        if user_type in ('admin', 'manager'):
            return CateringEvent.objects.all()
        # Staff and others only see approved events
        return CateringEvent.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        user_type = getattr(self.request.user, 'user_type', '')
        # Manager-created events need admin approval
        if user_type == 'manager':
            instance = serializer.save(is_approved=False)
        else:
            instance = serializer.save(is_approved=True)
        
        if user_type == 'manager':
            from .models import ActivityLog
            ActivityLog.objects.create(
                user=self.request.user,
                action=f"Created Booking: {instance.title}",
                details=(
                    f"Client: {instance.title}\n"
                    f"Date: {instance.date}\n"
                    f"Guests: {instance.guests}\n"
                    f"Venue: {getattr(instance, 'venue', '-')}\n"
                    f"Contact: {getattr(instance, 'contact_number', '-')}\n"
                    f"Event ID: {instance.id}"
                ),
                related_type='booking',
                related_id=instance.id,
                related_date=instance.date
            )

    def perform_update(self, serializer):
        instance = serializer.save()
        if getattr(self.request.user, 'user_type', '') == 'manager':
            from .models import ActivityLog
            ActivityLog.objects.create(
                user=self.request.user,
                action=f"Updated Booking: {instance.title}",
                details=(
                    f"Client: {instance.title}\n"
                    f"Date: {instance.date}\n"
                    f"Guests: {instance.guests}\n"
                    f"Event ID: {instance.id}"
                ),
                related_type='booking',
                related_id=instance.id,
                related_date=instance.date
            )

    def perform_destroy(self, instance):
        if getattr(self.request.user, 'user_type', '') == 'manager':
            from .models import ActivityLog
            ActivityLog.objects.create(
                user=self.request.user,
                action=f"Deleted Event {instance.id}",
                details=f"Event was on {instance.date}",
                related_type='event',
                related_id=instance.id,
                related_date=instance.date
            )
        super().perform_destroy(instance)

# --- 5. NEW TRACKER VIEWSETS ---

class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

class MemberLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemberLog.objects.all().order_by('-date')
    serializer_class = MemberLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset
    
class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def perform_create(self, serializer):
        user_type = getattr(self.request.user, 'user_type', '')
        if user_type == 'manager':
            instance = serializer.save(is_approved=False)
        else:
            instance = serializer.save(is_approved=True)
        
        if user_type == 'manager':
            from .models import ActivityLog
            event = getattr(instance, 'event', None)
            ActivityLog.objects.create(
                user=self.request.user,
                action=f"Created Menu: {instance.title}",
                details=(
                    f"Menu: {instance.title}\n"
                    f"Client: {event.title if event else '-'}\n"
                    f"Date: {event.date if event else '-'}\n"
                    f"Event ID: {event.id if event else 'None'}\n"
                    f"Menu ID: {instance.id}"
                ),
                related_type='menu',
                related_id=instance.id,
                related_date=getattr(event, 'date', None) if event else None
            )

    def perform_destroy(self, instance):
        if getattr(self.request.user, 'user_type', '') == 'manager':
            from .models import ActivityLog
            ActivityLog.objects.create(
                user=self.request.user,
                action=f"Deleted Menu {instance.id}",
                details=f"For event: {getattr(instance.event, 'id', 'None')}",
                related_type='menu',
                related_id=instance.id
            )
        super().perform_destroy(instance)

# --- 6. BOOKING API VIEW ---
@csrf_exempt
def book_event_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # 1. Save to Database
            booking = Booking.objects.create(
                name=data.get('name'),
                phone=data.get('phone'),
                event_date=data.get('date'),
                guest_count=data.get('guest_count'),
                event_type=data.get('event_type'),
                meal_time=data.get('meal_time'),
                package_type=data.get('package_type'),
                venue=data.get('venue'),
                message=data.get('message'),
                # Gujarati / Bilingual fields
                name_gu=data.get('name_gu', ''),
                venue_gu=data.get('venue_gu', ''),
            )
            booking.save()

            # 2. Prepare Email Content
            subject = f"New Booking Enquiry: {data.get('name')}"
            message = f"""
            New Booking Received from Swagat Caterers Website:
            
            Name: {data.get('name')}
            Phone: {data.get('phone')}
            Date: {data.get('date')}
            Guests: {data.get('guest_count')}
            Event Type: {data.get('event_type')}
            Package: {data.get('package_type')}
            
            Message:
            {data.get('message')}
            """

            # 3. Send Email (To Yourself)
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # From email
                [settings.EMAIL_HOST_USER], # To email (send to yourself)
                fail_silently=True,
            )

            # Log Manager Action
            if request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'manager':
                from .models import ActivityLog
                from datetime import datetime as dt
                booking_date = None
                try:
                    booking_date = dt.strptime(data.get('date', ''), '%Y-%m-%d').date()
                except Exception:
                    pass
                ActivityLog.objects.create(
                    user=request.user,
                    action=f"Created booking for {data.get('name')}",
                    details=f"Date: {data.get('date')} | Guests: {data.get('guest_count')} | Phone: {data.get('phone', '-')}",
                    related_type='booking',
                    related_id=booking.id,
                    related_date=booking_date
                )

            return JsonResponse({'status': 'success', 'message': 'Booking Saved & Email Sent!'})

        except Exception as e:
            print("Error:", e)
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# --- 7. SEND ENQUIRY EMAIL VIEW ---
@csrf_exempt
def send_enquiry_email(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            client_name = data.get('name', 'Website Visitor')
            client_phone = data.get('phone', 'Not provided')
            message_body = data.get('message', '')
            subject = data.get('subject', 'New Enquiry from Website')

            email_message = f"""
New Enquiry Received!
---------------------
Name: {client_name}
Phone: {client_phone}

Order Details:
{message_body}
            """

            send_mail(
                subject,
                email_message,
                settings.DEFAULT_FROM_EMAIL,
                ['swagatcaterersofficial@gmail.com'],
                fail_silently=True,
            )

            return JsonResponse({'status': 'success', 'message': 'Email sent successfully!'})

        except Exception as e:
            print(f"Email Error: {e}") 
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

# --- 8. MANUAL SESSION LOGIN FOR DJOSER ---
@api_view(['POST'])
@permission_classes([AllowAny])
def manual_session_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    # This uses your custom backend to check Email/Phone/Username
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        if user.is_active:
            # 1. Start the Session (This fixes the @login_required loop)
            login(request, user) 
            
            # 2. Get the Token (This keeps your Dashboard data working)
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'auth_token': token.key,
                'status': 'success'
            })
        return Response({'message': 'Account inactive'}, status=403)
    
    return Response({'message': 'Invalid credentials'}, status=401)
    
# --- 9. FRONTEND HOME VIEW ---
def frontend_home(request):
    from .models import Review, SampleTestimonial
    reviews = Review.objects.filter(is_featured=True).order_by('-created_at')[:6]
    samples = SampleTestimonial.objects.filter(is_active=True)
    return render(request, "index.html", {'reviews': reviews, 'sample_testimonials': samples})

def index(request):
    from .models import Review, SampleTestimonial
    reviews = Review.objects.filter(is_featured=True).order_by('-created_at')[:6]
    samples = SampleTestimonial.objects.filter(is_active=True)
    return render(request, "index.html", {'reviews': reviews, 'sample_testimonials': samples})

def menu(request):
    return render(request, "menu.html")

def about(request):
    return render(request, "about.html")

def gallery(request):
    return render(request, "gallery.html")

def contact(request):
    return render(request, "contact.html")

def book_now(request):
    return render(request, "booknow.html")

def custom_menu(request):
    return render(request, "customize_menu.html")

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def registration_pending(request):
    return render(request, "registration_pending.html")

def login_page(request):
    return render(request, "login.html")

def signup_page(request):
    return render(request, "signup.html")

@login_required
def profile(request):
    return render(request, "profile.html")

@login_required
def tracker(request):
    return render(request, "tracker.html")

@login_required
def booking(request):
    event_id = request.GET.get('event_id')
    date_param = request.GET.get('date')
    
    # Passing them into the dictionary context "accesses" them for Pylance
    # and makes them available to your HTML template
    return render(request, "booking.html", {
        "event_id": event_id,
        "date_param": date_param
    })

@login_required
def direct_menu(request):
    return render(request, "direct_menu.html")

@login_required
def create_menu(request):
    return render(request, "create_menu.html")

@login_required
def print_bill(request):
    return render(request, "print_bill.html")


# =========================================
# NEW VIEWS — PLATFORM UPGRADE
# =========================================
from .models import (
    GalleryItem, MenuItemStats, ItemCoOccurrence,
    EventStaff, Attendance, EventReminder, TaskAssignment, UserLoginHistory
)
from .decorators import require_role, require_permission
from django.utils import timezone
from datetime import timedelta, date
import requests as http_requests


# --- PDF Logging API ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def log_pdf_download(request):
    try:
        from .models import PdfLog
        import os
        event_details = request.data.get('event_details', 'Direct Menu PDF (No specific event)')
        
        PdfLog.objects.create(
            generated_by=request.user,
            event_details=event_details
        )
        
        # Send email to Admin
        admin_email = os.getenv('ADMIN_ALERT_EMAIL')
        if admin_email:
            subject = "New PDF Downloaded"
            message = f"A PDF was just generated.\n\nGenerated by: {request.user.username}\nDetails: {event_details}"
            send_mail(subject, message, settings.EMAIL_HOST_USER, [admin_email], fail_silently=True)
            
        return Response({'status': 'logged'})
    except Exception as e:
        return Response({'error': str(e)}, status=500)

# --- 7. NOTIFICATIONS / DASHBOARD APIS ---
# --- SECTION 2: Gallery API ---
@api_view(['GET'])
@permission_classes([AllowAny])
def gallery_api(request):
    """Public API to list gallery items."""
    items = GalleryItem.objects.all()
    category = request.query_params.get('category')
    if category:
        items = items.filter(category=category)
    data = [{
        'id': item.id,
        'title': item.title,
        'category': item.category,
        'media_type': item.media_type,
        'url': item.media_url,
        'youtube_url': item.youtube_url,
        'created_at': item.created_at.isoformat(),
    } for item in items]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gallery_upload(request):
    """Upload gallery item (admin/manager only)."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    title = request.data.get('title', 'Untitled')
    category = request.data.get('category', 'other')
    media_type = request.data.get('media_type', 'image')
    youtube_url = request.data.get('youtube_url', '')

    item = GalleryItem(
        title=title,
        category=category,
        media_type=media_type,
        youtube_url=youtube_url,
        uploaded_by=request.user,
    )

    if 'image' in request.FILES:
        item.image = request.FILES['image']

    if request.data.get('cloudinary_url'):
        item.cloudinary_url = request.data['cloudinary_url']

    item.save()
    return Response({'status': 'success', 'id': item.id, 'message': 'Gallery item uploaded!'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def gallery_delete(request, item_id):
    """Delete a gallery item (admin/manager only)."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    try:
        item = GalleryItem.objects.get(id=item_id)
    except GalleryItem.DoesNotExist:
        return Response({'error': 'Item not found'}, status=404)

    # Delete the file from storage if it exists
    if item.image:
        try:
            item.image.delete(save=False)
        except Exception:
            pass

    item.delete()
    return Response({'status': 'success', 'message': 'Gallery item deleted!'})


@login_required
@require_role(['admin', 'manager'])
def gallery_manage(request):
    """Dashboard gallery management page."""
    return render(request, "gallery_manage.html")


# --- SECTION 3: Public Booking Status Tracker ---
def booking_status(request, token):
    """Public booking status tracker - no login required."""
    event = get_object_or_404(CateringEvent, tracking_token=token)
    
    # Only expose safe data
    manager_name = ''
    if event.assigned_manager:
        manager_name = event.assigned_manager.first_name or 'Your Manager'

    context = {
        'event_name': event.title,
        'event_date': event.date,
        'status': event.status,
        'manager_name': manager_name,
        'tracking_token': str(token),
    }
    return render(request, "public/booking_status.html", context)


# --- SECTION 4: Calendar API ---
@api_view(['GET'])
@permission_classes([AllowAny])
def calendar_api(request):
    """Returns events for FullCalendar.js. Public view hides client names and restricts to 120 days."""
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    max_date = today + timedelta(days=120)
    
    events = CateringEvent.objects.filter(date__gte=today, date__lte=max_date, is_approved=True)
    
    is_authenticated = request.user.is_authenticated

    color_map = {
        'confirmed': '#e74c3c',
        'in_progress': '#e74c3c',
        'received': '#f39c12',
        'pending': '#f39c12',
        'completed': '#27ae60',
        'cancelled': '#95a5a6',
    }

    data = []
    for event in events:
        # Everyone sees generic titles on public calendar to protect privacy
        title = 'Booked' if event.status in ('confirmed', 'in_progress') else 'Pending'
        
        data.append({
            'title': title,
            'start': event.date.isoformat(),
            'end': event.date.isoformat(),
            'status': event.status,
            'color': color_map.get(event.status, '#e67e22'),
            'id': event.id if is_authenticated else None,
        })

    return Response(data)


def calendar_public(request):
    """Public calendar page showing availability."""
    return render(request, "calendar_public.html")


# --- SECTION 5: Weather-Based Menu Suggestions ---
@api_view(['GET'])
@permission_classes([AllowAny])
def weather_suggest(request):
    """Get weather-based menu suggestions for a city and date."""
    city = request.query_params.get('city', '')
    event_date = request.query_params.get('date', '')

    if not city:
        return Response({'error': 'City is required'}, status=400)

    api_key = settings.OPENWEATHERMAP_API_KEY
    if not api_key:
        return Response({
            'weather_summary': 'Weather service not configured',
            'icon': '🌤️',
            'suggested_items': [],
            'tip': 'Contact us for personalized menu suggestions!'
        })

    try:
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={api_key}&units=metric'
        resp = http_requests.get(url, timeout=5)
        data = resp.json()

        if resp.status_code != 200:
            return Response({
                'weather_summary': f'Could not fetch weather for {city}',
                'icon': '❓',
                'suggested_items': [],
                'tip': 'Try a different city name.'
            })

        temp = data.get('main', {}).get('temp', 25)
        weather_main = data.get('weather', [{}])[0].get('main', '').lower()
        icon_code = data.get('weather', [{}])[0].get('icon', '01d')

        # Determine suggestions based on weather
        if temp < 20 or 'rain' in weather_main or 'drizzle' in weather_main:
            suggested = ['Hot Tomato Soup', 'Masala Chai', 'Pakoda', 'Warm Starters', 'Gajar Halwa', 'Hot Jalebi']
            tip = f'🌧️ Expected {temp:.0f}°C with {weather_main}. Warm items recommended!'
            icon = '🌧️'
        elif temp > 35:
            suggested = ['Cold Coffee', 'Jaljeera', 'Ice Cream', 'Fruit Salad', 'Buttermilk', 'Light Salads']
            tip = f'☀️ Expected {temp:.0f}°C — hot weather! Chilled items will be perfect.'
            icon = '🔥'
        else:
            suggested = ['Mixed Starters', 'Paneer Tikka', 'Dal Makhani', 'Gulab Jamun', 'Lassi', 'Biryani']
            tip = f'🌤️ Pleasant {temp:.0f}°C weather. Standard menu works great!'
            icon = '🌤️'

        return Response({
            'weather_summary': f'{temp:.0f}°C, {weather_main.title()} in {city}',
            'icon': icon,
            'suggested_items': suggested,
            'tip': tip,
            'temp': temp,
        })

    except Exception as e:
        return Response({
            'weather_summary': 'Weather service unavailable',
            'icon': '⚠️',
            'suggested_items': [],
            'tip': str(e)
        })


# --- SECTION 6: Internal Notes AJAX Save ---
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_internal_notes(request, event_id):
    """AJAX save internal notes for an event (admin/manager only)."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    event = get_object_or_404(CateringEvent, id=event_id)
    notes = request.data.get('notes', '')

    event.internal_notes = notes
    event.notes_updated_by = request.user
    event.notes_updated_at = timezone.now()
    event.save(update_fields=['internal_notes', 'notes_updated_by', 'notes_updated_at'])

    return Response({
        'status': 'success',
        'message': f'Saved by {request.user.username} at {timezone.now().strftime("%H:%M")}',
        'updated_at': event.notes_updated_at.isoformat(),
    })


# --- SECTION 3: Update Event Status ---
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_event_status(request, event_id):
    """Update event status (admin/manager only)."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    event = get_object_or_404(CateringEvent, id=event_id)
    new_status = request.data.get('status')

    valid_statuses = [s[0] for s in CateringEvent.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=400)

    event.status = new_status
    event.save(update_fields=['status'])

    # Log Manager Action
    if user_type == 'manager':
        from .models import ActivityLog
        ActivityLog.objects.create(
            user=request.user,
            action=f"Updated status of Event {event.id} to {new_status}",
            details=f"Date: {event.date}",
            related_type='event',
            related_id=event.id,
            related_date=event.date
        )

    return Response({
        'status': 'success',
        'new_status': new_status,
        'message': f'Status updated to {new_status}',
    })


# --- SECTION 13: Staff Scheduling Views ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_staff_api(request, event_id):
    """Manage staff assignments for an event."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager', 'event_manager'):
        return Response({'error': 'Permission denied'}, status=403)

    event = get_object_or_404(CateringEvent, id=event_id)

    if request.method == 'GET':
        assignments = EventStaff.objects.filter(event=event).select_related('member')
        data = [{
            'id': a.id,
            'member_id': a.member.id,
            'member_name': a.member.username,
            'role': a.role,
            'confirmed': a.confirmed,
            'has_conflict': False,
        } for a in assignments]
        return Response(data)

    if request.method == 'POST':
        member_id = request.data.get('member_id')
        role = request.data.get('role', 'server')
        confirmed = request.data.get('confirmed', False)

        User = get_user_model()
        member = get_object_or_404(User, id=member_id)

        assignment = EventStaff(event=event, member=member, role=role, confirmed=confirmed)
        try:
            assignment.full_clean()
            assignment.save()
            return Response({'status': 'success', 'id': assignment.id})
        except Exception as e:
            return Response({'error': str(e)}, status=400)


# --- My Tasks Page ---
@login_required
def my_tasks_page(request):
    """Dedicated page for staff/managers to see and manage their assigned tasks."""
    return render(request, 'my_tasks.html')


# --- SECTION 15: Task Assignment Views ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_api(request):
    """List/create tasks."""
    user = request.user
    user_type = getattr(user, 'user_type', 'customer')

    if request.method == 'GET':
        # ?my=true returns only tasks assigned to the current user (for the floating widget)
        my_only = request.query_params.get('my', '').lower() == 'true'

        if user_type == 'admin' and not my_only:
            tasks = TaskAssignment.objects.all()
        else:
            # Manager, Staff, or admin with ?my=true see only tasks assigned to them
            tasks = TaskAssignment.objects.filter(assigned_to=user)

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)

        assignee_filter = request.query_params.get('assignee')
        if assignee_filter:
            tasks = tasks.filter(assigned_to_id=assignee_filter)

        data = [{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'deadline': t.deadline.isoformat(),
            'priority': t.priority,
            'status': t.status,
            'assigned_by': t.assigned_by.username,
            'assigned_to': t.assigned_to.id,
            'assigned_to_name': t.assigned_to.username,
            'assigned_to_id': t.assigned_to.id,
            'is_overdue': t.is_overdue,
            'created_at': t.created_at.isoformat(),
        } for t in tasks]
        return Response(data)

    if request.method == 'POST':
        if user_type not in ('admin', 'manager'):
            return Response({'error': 'Only admin/manager can assign tasks'}, status=403)

        User = get_user_model()
        assigned_to = get_object_or_404(User, id=request.data.get('assigned_to'))

        task = TaskAssignment.objects.create(
            assigned_by=user,
            assigned_to=assigned_to,
            title=request.data.get('title', ''),
            description=request.data.get('description', ''),
            deadline=request.data.get('deadline'),
            priority=request.data.get('priority', 'medium'),
        )

        # Send attractive HTML email notification
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.utils import timezone

            priority_colors = {'high': '#e74c3c', 'medium': '#f39c12', 'low': '#27ae60'}
            priority_labels = {'high': '🔴 High Priority', 'medium': '🟡 Medium', 'low': '🟢 Low'}
            prio_color = priority_colors.get(task.priority, '#999')
            prio_label = priority_labels.get(task.priority, task.priority)
            deadline_str = task.deadline.strftime('%d %B %Y') if task.deadline else 'No deadline'

            html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:30px 15px;">
<tr><td align="center">
<table width="100%" cellpadding="0" cellspacing="0" style="max-width:520px;background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">

  <!-- Header -->
  <tr><td style="background:linear-gradient(135deg,#1a1a1a,#2c2c2c);padding:28px 30px;text-align:center;">
    <h1 style="margin:0;color:#D4AF37;font-size:22px;font-weight:700;letter-spacing:0.5px;">📋 New Task Assigned</h1>
    <p style="margin:8px 0 0;color:rgba(255,255,255,0.6);font-size:13px;">Swagat Caterers — Task Management</p>
  </td></tr>

  <!-- Greeting -->
  <tr><td style="padding:28px 30px 10px;">
    <p style="margin:0;color:#333;font-size:16px;">Hi <strong>{assigned_to.username}</strong>,</p>
    <p style="margin:8px 0 0;color:#666;font-size:14px;line-height:1.5;">You have been assigned a new task by <strong>{user.username}</strong>. Please review the details below.</p>
  </td></tr>

  <!-- Task Card -->
  <tr><td style="padding:15px 30px;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#faf9f6;border:1px solid #f0ece4;border-radius:10px;border-left:4px solid {prio_color};">
      <tr><td style="padding:20px;">
        <h2 style="margin:0 0 12px;color:#1a1a1a;font-size:18px;font-weight:700;">{task.title}</h2>
        {'<p style="margin:0 0 14px;color:#666;font-size:13px;line-height:1.5;">' + task.description + '</p>' if task.description else ''}
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:6px 0;">
              <span style="color:#999;font-size:12px;">Priority</span><br>
              <span style="display:inline-block;margin-top:4px;padding:3px 12px;border-radius:12px;font-size:12px;font-weight:700;color:#fff;background:{prio_color};">{prio_label}</span>
            </td>
            <td style="padding:6px 0;">
              <span style="color:#999;font-size:12px;">Deadline</span><br>
              <span style="color:#1a1a1a;font-size:14px;font-weight:600;margin-top:4px;display:inline-block;">📅 {deadline_str}</span>
            </td>
          </tr>
          <tr>
            <td colspan="2" style="padding:10px 0 0;">
              <span style="color:#999;font-size:12px;">Assigned By</span><br>
              <span style="color:#1a1a1a;font-size:14px;font-weight:600;margin-top:4px;display:inline-block;">👤 {user.username}</span>
            </td>
          </tr>
        </table>
      </td></tr>
    </table>
  </td></tr>

  <!-- CTA Button -->
  <tr><td style="padding:10px 30px 25px;text-align:center;">
    <a href="https://swagatcaterers.in/my-tasks/" style="display:inline-block;background:linear-gradient(135deg,#D4AF37,#c5a028);color:#1a1a1a;padding:13px 35px;border-radius:8px;text-decoration:none;font-weight:700;font-size:14px;box-shadow:0 3px 12px rgba(212,175,55,0.3);">View My Tasks →</a>
  </td></tr>

  <!-- Footer -->
  <tr><td style="background:#faf9f6;padding:18px 30px;text-align:center;border-top:1px solid #f0ece4;">
    <p style="margin:0;color:#999;font-size:11px;">🍽️ Swagat Caterers · Task Management System</p>
    <p style="margin:5px 0 0;color:#bbb;font-size:10px;">This is an automated notification. Please do not reply to this email.</p>
  </td></tr>

</table>
</td></tr>
</table>
</body>
</html>"""

            plain_text = (
                f"Hi {assigned_to.username},\n\n"
                f"You have been assigned a new task by {user.username}.\n\n"
                f"Title: {task.title}\n"
                f"Description: {task.description or 'N/A'}\n"
                f"Deadline: {deadline_str}\n"
                f"Priority: {task.priority}\n\n"
                f"Log in to view: https://swagatcaterers.in/my-tasks/"
            )

            msg = EmailMultiAlternatives(
                subject=f'📋 New Task: {task.title} — Swagat Caterers',
                body=plain_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[assigned_to.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=True)
        except Exception:
            pass

        return Response({'status': 'success', 'id': task.id})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def task_update_status(request, task_id):
    """Update task status (assignee can update to in_progress/done)."""
    task = get_object_or_404(TaskAssignment, id=task_id)
    user = request.user

    # Only assignee, admin, or manager can update
    if task.assigned_to != user and getattr(user, 'user_type', '') not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    new_status = request.data.get('status')
    if new_status not in ('pending', 'in_progress', 'done', 'rejected'):
        return Response({'error': 'Invalid status'}, status=400)

    task.status = new_status
    task.save(update_fields=['status', 'updated_at'])

    return Response({'status': 'success', 'new_status': new_status})


# --- SECTION 17: Notes API (All Roles) ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_notes_api(request):
    """
    GET: Admin sees ALL notes. Manager/Staff see only their own notes.
    POST: Any authenticated user can create a note.
    Notes auto-delete after 60 days.
    """
    from .models import AdminNote
    from django.utils import timezone
    from datetime import timedelta
    
    # Auto-delete notes older than 60 days
    sixty_days_ago = timezone.now().date() - timedelta(days=60)
    AdminNote.objects.filter(note_date__lt=sixty_days_ago).delete()
    
    if request.method == 'GET':
        user_type = getattr(request.user, 'user_type', 'customer')
        if user_type == 'admin':
            # Admin sees ALL notes from everyone
            notes = AdminNote.objects.all().select_related('author')[:100]
        else:
            # Manager/Staff see only their own notes
            notes = AdminNote.objects.filter(author=request.user)[:50]
        
        data = [{
            'id': n.id,
            'content': n.content,
            'note_type': n.note_type,
            'author_name': n.author.username,
            'author_type': getattr(n.author, 'user_type', 'unknown'),
            'event_id': n.event_id,
            'note_date': str(n.note_date),
            'created_at': n.created_at.isoformat(),
        } for n in notes]
        return Response(data)
    
    if request.method == 'POST':
        note_date_str = request.data.get('note_date')
        if note_date_str:
            note_date = note_date_str
        else:
            note_date = timezone.now().date()

        note = AdminNote.objects.create(
            author=request.user,
            content=request.data.get('content', ''),
            note_type=request.data.get('note_type', 'general'),
            event_id=request.data.get('event_id'),
            note_date=note_date
        )
        return Response({'status': 'success', 'id': note.id})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_note_delete(request, note_id):
    """Delete a note. Users can delete their own. Admin can delete any."""
    from .models import AdminNote
    try:
        note = AdminNote.objects.get(id=note_id)
    except AdminNote.DoesNotExist:
        return Response({'error': 'Note not found'}, status=404)
    
    user_type = getattr(request.user, 'user_type', 'customer')
    if note.author != request.user and user_type != 'admin':
        return Response({'error': 'Permission denied'}, status=403)
    
    note.delete()
    return Response({'status': 'success'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_notes_download(request):
    """Download all notes as CSV. Admin only."""
    from .models import AdminNote
    import csv
    from django.http import HttpResponse as DjangoHttpResponse
    
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type != 'admin':
        return Response({'error': 'Permission denied'}, status=403)
    
    notes = AdminNote.objects.all().select_related('author')
    
    response = DjangoHttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="swagat_notes_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Author', 'Role', 'Date', 'Content', 'Type', 'Created At'])
    
    for n in notes:
        writer.writerow([
            n.author.username,
            getattr(n.author, 'user_type', 'unknown'),
            str(n.note_date),
            n.content,
            n.note_type,
            str(n.created_at),
        ])
    
    return response


# --- Staff/Manager Users API (for task assignment dropdown) ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_users_api(request):
    """Return list of staff and manager users for task assignment."""
    User = get_user_model()
    users = User.objects.filter(user_type__in=['staff', 'manager']).values(
        'id', 'username', 'user_type', 'email', 'phone_number'
    )
    return Response(list(users))


# --- Admin: Delete Staff/Manager User ---
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, user_id):
    """Admin-only: Delete a staff/manager user and ALL their data."""
    if not (request.user.is_superuser or getattr(request.user, 'user_type', '') == 'admin'):
        return Response({'error': 'Admin access required'}, status=403)
    
    UserModel = get_user_model()
    try:
        target_user = UserModel.objects.get(id=user_id)
    except UserModel.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    
    # Prevent deleting admin users
    if target_user.is_superuser or target_user.user_type == 'admin':
        return Response({'error': 'Cannot delete admin users'}, status=403)
    
    username = target_user.username
    
    # Clean up CharField-based references (not FK, so no cascade)
    # Menus created by this user
    Menu.objects.filter(created_by=username).update(created_by='[deleted]')
    
    # Activity logs are automatically deleted via Django CASCADE
    
    # Delete the user — Django CASCADE will handle FK relationships:
    # - StaffAssignment (member FK → Member, not User directly)
    # - Task (assigned_to FK → User) 
    # - LoginHistory (user FK → User)
    # - Notification (user FK → User)
    # - EventComment (author FK → User)
    target_user.delete()
    
    return Response({
        'success': True, 
        'message': f'User "{username}" and all associated data deleted successfully.'
    })


# --- Activity Review Page ---
@login_required
def activity_review_page(request):
    """Dedicated page for admin to review manager activity logs."""
    return render(request, 'activity_review.html')


# --- Assign Tasks Page (Admin only) ---
@login_required
def assign_tasks_page(request):
    """Dedicated page for admin to assign and manage tasks."""
    return render(request, 'assign_tasks.html')


# --- Staff Menu Viewer Page (View-only, no download) ---
@login_required
def view_menu_page(request):
    """Read-only menu viewer page for staff in both languages."""
    return render(request, 'view_menu.html')


# --- SECTION 18: Activity Logs API (Manager Actions) ---
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def activity_logs_api(request):
    """
    GET: Admin sees activity logs. ?show_all=true for all logs, default only unreviewed.
    POST: Admin marks a log as reviewed (hidden).
    """
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type != 'admin':
        return Response({'error': 'Permission denied'}, status=403)

    from .models import ActivityLog

    if request.method == 'GET':
        show_all = request.query_params.get('show_all', 'false') == 'true'
        if show_all:
            logs = ActivityLog.objects.exclude(related_type='menu').select_related('user')[:100]
        else:
            logs = ActivityLog.objects.filter(is_reviewed=False).exclude(related_type='menu').select_related('user')[:50]
        data = [{
            'id': log.id,
            'username': log.user.username,
            'user_type': getattr(log.user, 'user_type', 'unknown'),
            'action': log.action,
            'details': log.details,
            'is_reviewed': log.is_reviewed,
            'related_type': log.related_type or 'other',
            'related_id': log.related_id,
            'related_date': str(log.related_date) if log.related_date else None,
            'created_at': log.created_at.isoformat()
        } for log in logs]
        return Response(data)
    
    if request.method == 'POST':
        # Mark log as reviewed AND approve the related event/menu
        log_id = request.data.get('log_id')
        if log_id:
            try:
                log = ActivityLog.objects.get(id=log_id)
                log.is_reviewed = True
                log.save(update_fields=['is_reviewed'])

                # Auto-approve the related booking/menu
                if log.related_type == 'booking' and log.related_id:
                    try:
                        event = CateringEvent.objects.get(id=log.related_id)
                        if not event.is_approved:
                            event.is_approved = True
                            event.save(update_fields=['is_approved'])
                    except CateringEvent.DoesNotExist:
                        pass
                elif log.related_type == 'menu' and log.related_id:
                    try:
                        menu = Menu.objects.get(id=log.related_id)
                        if not menu.is_approved:
                            menu.is_approved = True
                            menu.save(update_fields=['is_approved'])
                    except Menu.DoesNotExist:
                        pass

                return Response({'status': 'success', 'approved': True})
            except ActivityLog.DoesNotExist:
                return Response({'error': 'Log not found'}, status=404)
        return Response({'error': 'Log ID required'}, status=400)


# --- SECTION 4: Menu Items List API (for calendar/recommendations) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def menu_items_public(request):
    """Public API for menu items (used by calendar + recommendations)."""
    items = Menu_item.objects.select_related('category').all()
    data = [{
        'id': item.id,
        'name': item.name,
        'gujarati_name': item.gujarati_name or '',
        'category': item.category.name,
        'category_id': item.category.id,
        'image': item.image.url if item.image else '',
    } for item in items]
    return Response(data)


# --- SECTION 4: Events List API (for calendar) ---
@api_view(['GET'])
@permission_classes([AllowAny])
def events_list_public(request):
    """Public API listing events (minimal info for calendar)."""
    events = CateringEvent.objects.all()
    data = [{
        'id': e.id,
        'title': 'Booked' if e.status in ('confirmed', 'in_progress') else 'Available',
        'date': e.date.isoformat(),
        'status': e.status,
    } for e in events]
    return Response(data)





# --- SECTION 9: AI Menu Recommendation Engine ---
@api_view(['GET'])
@permission_classes([AllowAny])
def menu_recommend(request):
    """Recommend menu items based on event type, guest count, and season."""
    event_type = request.GET.get('event_type', 'wedding')
    guests = int(request.GET.get('guests', 100))
    month = request.GET.get('month', '')

    # Build smart recommendations based on event type
    type_tags = {
        'wedding': ['paneer', 'dal', 'rice', 'sweet', 'starter', 'puri'],
        'corporate': ['sandwich', 'pasta', 'salad', 'soup', 'juice'],
        'birthday': ['pizza', 'cake', 'sweet', 'starter', 'ice cream'],
        'engagement': ['paneer', 'biryani', 'sweet', 'starter', 'kulfi'],
        'thread_ceremony': ['puri', 'dal', 'rice', 'sweet', 'khichdi'],
    }

    # Get items matching the event type tags
    tags = type_tags.get(event_type.lower(), type_tags['wedding'])
    from django.db.models import Q
    q = Q()
    for tag in tags:
        q |= Q(name__icontains=tag) | Q(gujarati_name__icontains=tag)

    recommended = Menu_item.objects.filter(q).distinct()[:12]

    # Also get popular items from MenuItemStats
    try:
        popular = MenuItemStats.objects.order_by('-booking_count')[:5]
        popular_items = [{'id': s.menu_item.id, 'name': s.menu_item.name, 'bookings': s.booking_count}
                        for s in popular if s.menu_item]
    except Exception:
        popular_items = []

    data = {
        'event_type': event_type,
        'guests': guests,
        'recommended': [{'id': i.id, 'name': i.name, 'gujarati_name': i.gujarati_name,
                         'category': i.category.name if i.category else ''} for i in recommended],
        'popular': popular_items,
        'tip': f"For a {event_type} with {guests} guests, we recommend {len(recommended)} curated items.",
    }
    return Response(data)


# --- SECTION 11: Also-Selected (Co-occurrence) API ---
@api_view(['GET'])
@permission_classes([AllowAny])
def also_selected_api(request, item_id):
    """Get items frequently ordered together with a given item."""
    from django.db.models import Q
    pairs = ItemCoOccurrence.objects.filter(
        Q(item_a_id=item_id) | Q(item_b_id=item_id)
    ).order_by('-count')[:6]

    results = []
    for pair in pairs:
        other = pair.item_b if pair.item_a_id == item_id else pair.item_a
        results.append({
            'id': other.id,
            'name': other.name,
            'gujarati_name': other.gujarati_name,
            'category': other.category.name if other.category else '',
            'co_count': pair.count,
        })

    return Response({'item_id': item_id, 'also_selected': results})


# --- SECTION 19: Login History + Logout All ---
@login_required
def login_history_page(request):
    """Render login history page."""
    return render(request, 'login_history.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def login_history_api(request):
    """Get login history for the current user with parsed device info."""
    import re
    
    def parse_user_agent(ua):
        if not ua:
            return {'browser': 'Unknown', 'os': 'Unknown', 'device': 'Unknown'}
        
        # Browser detection
        browser = 'Unknown'
        if 'Edg/' in ua: browser = 'Edge'
        elif 'OPR/' in ua or 'Opera' in ua: browser = 'Opera'
        elif 'Chrome/' in ua and 'Safari/' in ua: browser = 'Chrome'
        elif 'Firefox/' in ua: browser = 'Firefox'
        elif 'Safari/' in ua: browser = 'Safari'
        elif 'MSIE' in ua or 'Trident/' in ua: browser = 'IE'
        
        # OS detection
        os_name = 'Unknown'
        if 'Windows NT 10' in ua: os_name = 'Windows 10/11'
        elif 'Windows NT' in ua: os_name = 'Windows'
        elif 'Mac OS X' in ua: os_name = 'macOS'
        elif 'Android' in ua:
            m = re.search(r'Android ([\d.]+)', ua)
            os_name = f"Android {m.group(1)}" if m else 'Android'
        elif 'iPhone' in ua or 'iPad' in ua: os_name = 'iOS'
        elif 'Linux' in ua: os_name = 'Linux'
        
        # Device type
        device = 'Desktop'
        if any(x in ua.lower() for x in ['mobile', 'android', 'iphone', 'ipod']):
            device = 'Mobile'
        elif 'ipad' in ua.lower() or 'tablet' in ua.lower():
            device = 'Tablet'
        
        return {'browser': browser, 'os': os_name, 'device': device}
    
    # Admin sees all users' history, regular user sees only their own
    if request.user.is_staff:
        history = UserLoginHistory.objects.select_related('user').order_by('-timestamp')[:100]
    else:
        history = UserLoginHistory.objects.filter(user=request.user).order_by('-timestamp')[:50]
    
    data = []
    for h in history:
        parsed = parse_user_agent(h.user_agent)
        entry = {
            'ip': h.ip_address,
            'user_agent': h.user_agent[:80] if h.user_agent else '',
            'browser': parsed['browser'],
            'os': parsed['os'],
            'device': parsed['device'],
            'city': h.city,
            'country': h.country,
            'is_new_ip': h.is_new_ip,
            'timestamp': h.timestamp.isoformat(),
        }
        if request.user.is_staff:
            entry['username'] = h.user.username
        data.append(entry)
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_sessions(request):
    """Invalidate all auth tokens for this user (logout everywhere)."""
    from rest_framework.authtoken.models import Token
    Token.objects.filter(user=request.user).delete()
    # Create a fresh token for the current session
    new_token = Token.objects.create(user=request.user)
    return Response({'message': 'All other sessions logged out.', 'new_token': new_token.key})


# --- SECTION 23: Review System ---

def review_page(request, token):
    """Public review page — no login required."""
    event = get_object_or_404(CateringEvent, review_token=token)
    
    # Check if review already exists
    existing_review = None
    try:
        existing_review = event.review
    except:
        pass
    
    return render(request, 'public/review.html', {
        'event': event,
        'existing_review': existing_review,
        'token': token,
    })


@csrf_exempt
def submit_review(request, token):
    """API to submit a review — no login required."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    event = get_object_or_404(CateringEvent, review_token=token)
    
    # Check if review already exists
    try:
        if event.review:
            return JsonResponse({'error': 'Review already submitted for this event'}, status=400)
    except:
        pass
    
    try:
        data = json.loads(request.body)
        reviewer_name = data.get('reviewer_name', '').strip()
        rating = int(data.get('rating', 0))
        review_text = data.get('review_text', '').strip()
        
        if not reviewer_name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        if rating < 1 or rating > 5:
            return JsonResponse({'error': 'Rating must be 1-5'}, status=400)
        
        from .models import Review
        review = Review.objects.create(
            event=event,
            reviewer_name=reviewer_name,
            rating=rating,
            review_text=review_text
        )
        
        # Send email notification to admin
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            stars = '★' * rating + '☆' * (5 - rating)
            admin_email = getattr(settings, 'ADMIN_ALERT_EMAIL', getattr(settings, 'ADMIN_EMAIL', ''))
            
            if admin_email:
                send_mail(
                    subject=f'⭐ New Review: {stars} by {reviewer_name}',
                    message=(
                        f'New Review Received!\n\n'
                        f'Reviewer: {reviewer_name}\n'
                        f'Rating: {stars} ({rating}/5)\n'
                        f'Event: {event.title} ({event.event_type})\n'
                        f'Event Date: {event.date}\n\n'
                        f'Review:\n"{review_text}"\n\n'
                        f'---\n'
                        f'Manage reviews at: https://swagatcaterers.in/reviews/\n'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[admin_email],
                    fail_silently=True,
                )
                review.email_notified = True
                review.save()
        except Exception as email_err:
            print(f"Review email notification failed: {email_err}")
        
        return JsonResponse({'success': True, 'message': 'Thank you for your review!'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# --- SECTION 24: WhatsApp URL Generator (Server-side emoji encoding) ---

from urllib.parse import quote

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whatsapp_booking_url(request, event_id):
    """Generate WhatsApp booking confirmation URL with proper emoji encoding."""
    event = get_object_or_404(CateringEvent, id=event_id)
    
    phone = (event.contact_number or '').replace(' ', '').replace('-', '').replace('+', '')
    if len(phone) == 10:
        phone = '91' + phone
    
    if not phone:
        return JsonResponse({'error': 'No contact number'}, status=400)
    
    date_str = event.date.strftime('%d-%m-%Y')
    venue = event.venue or 'Not Specified'
    event_type = event.event_type or 'Event'
    guests = event.guests or '-'

    message = f"""🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉

🍽️ *SWAGAT CATERERS*
_Premium Catering • Rajkot_

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉

✅ *BOOKING CONFIRMED!*

Hello *{event.title}*,

Your booking is confirmed! We're excited to serve you 🔥

📅 *Date:* {date_str}
📍 *Venue:* {venue}
🎊 *Event:* {event_type}
👥 *Guests:* {guests}

🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉

Our team will make your {event_type.lower()} truly special! ✨

📞 *+91 94282 51083*
🌐 *swagatcaterers.in*

🙏 _Thank you for choosing Swagat!_"""

    whatsapp_url = (
        f"https://api.whatsapp.com/send"
        f"?phone={phone}"
        f"&text={quote(message, safe='')}"
    )
    return JsonResponse({'url': whatsapp_url})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def whatsapp_review_url(request, event_id):
    """Generate WhatsApp review request URL with proper emoji encoding."""
    event = get_object_or_404(CateringEvent, id=event_id)
    
    phone = (event.contact_number or '').replace(' ', '').replace('-', '').replace('+', '')
    if len(phone) == 10:
        phone = '91' + phone
    
    if not phone:
        return JsonResponse({'error': 'No contact number'}, status=400)
    
    date_str = event.date.strftime('%d-%m-%Y')
    event_type = event.event_type or 'Event'
    review_token = str(event.review_token)
    platform_link = f"https://swagatcaterers.in/review/{review_token}"
    google_maps_link = "https://g.page/r/CdwNh_v0ZuUcEBM/review"

    message = f"""🙏 *Namaste {event.title}!*

Hope you loved the food at your *{event_type}* on *{date_str}*! 🎊😋

⭐⭐⭐⭐⭐

We'd love your feedback! It takes just 30 seconds 👇

🌐 *Review on our Website:*
{platform_link}

📍 *Review on Google Maps:*
{google_maps_link}

Your words mean everything to us! 💛

🍽️ *Team Swagat Caterers*
📞 +91 94282 51083"""

    whatsapp_url = (
        f"https://api.whatsapp.com/send"
        f"?phone={phone}"
        f"&text={quote(message, safe='')}"
    )
    return JsonResponse({'url': whatsapp_url})


# --- SECTION 25: Review Management (Admin) ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_reviews_list(request):
    """List all reviews for admin management."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import Review
    reviews = Review.objects.select_related('event').order_by('-created_at')
    data = []
    for r in reviews:
        data.append({
            'id': r.id,
            'reviewer_name': r.reviewer_name,
            'rating': r.rating,
            'review_text': r.review_text,
            'is_featured': r.is_featured,
            'admin_response': r.admin_response,
            'response_at': r.response_at.isoformat() if r.response_at else None,
            'created_at': r.created_at.isoformat(),
            'event_title': r.event.title,
            'event_type': r.event.event_type or '',
            'event_date': r.event.date.strftime('%d-%m-%Y'),
        })
    return JsonResponse({'reviews': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_review_featured(request, review_id):
    """Toggle is_featured status for a review."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import Review
    review = get_object_or_404(Review, id=review_id)
    review.is_featured = not review.is_featured
    review.save()
    return JsonResponse({
        'id': review.id,
        'is_featured': review.is_featured,
        'message': f"Review {'featured' if review.is_featured else 'unfeatured'} successfully."
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_respond(request, review_id):
    """Admin responds to a review."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import Review
    from django.utils import timezone
    review = get_object_or_404(Review, id=review_id)
    data = json.loads(request.body)
    response_text = data.get('response', '').strip()
    
    review.admin_response = response_text
    review.response_at = timezone.now() if response_text else None
    review.save()
    
    return JsonResponse({
        'id': review.id,
        'admin_response': review.admin_response,
        'response_at': review.response_at.isoformat() if review.response_at else None,
        'message': 'Response saved.' if response_text else 'Response removed.'
    })


@login_required
def admin_reviews_page(request):
    """Render the admin reviews management page."""
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Admin only")
    return render(request, 'admin/reviews.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_backup(request):
    """Trigger a database backup via the backup_db management command."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
        
    try:
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('backup_db', stdout=out)
        
        return JsonResponse({
            'success': True,
            'message': 'Database backup completed successfully!',
            'output': out.getvalue()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_backups(request):
    """List all available database backups."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
        
    from django.conf import settings
    from pathlib import Path
    import os
    
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    if not backup_dir.exists():
        return JsonResponse({'backups': []})
        
    backups = []
    for b in sorted(backup_dir.glob('swagat_db_*'), key=lambda p: p.stat().st_mtime, reverse=True):
        stat = b.stat()
        backups.append({
            'filename': b.name,
            'size_mb': round(stat.st_size / (1024 * 1024), 2),
            'timestamp': stat.st_mtime,
        })
        
    return JsonResponse({'backups': backups})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_backup(request, filename):
    """Securely download a specific database backup."""
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Admin only")
        
    from django.conf import settings
    from django.http import FileResponse, Http404
    from pathlib import Path
    import os
    
    # Security check: only allow word chars, dots, hyphens, and underscores
    import re
    if not re.match(r'^[\w\-\.]+$', filename):
        raise Http404("Invalid filename")
        
    backup_path = Path(settings.BASE_DIR) / 'backups' / filename
    
    if not backup_path.exists() or not backup_path.is_file():
        raise Http404("Backup file not found")
        
    response = FileResponse(open(backup_path, 'rb'), as_attachment=True, filename=filename)
    return response


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_backup(request, filename):
    """Securely delete a specific database backup."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
        
    from django.conf import settings
    from pathlib import Path
    import os
    import re
    
    # Security check: only allow word chars, dots, hyphens, and underscores
    if not re.match(r'^[\w\-\.]+$', filename):
        return JsonResponse({'error': 'Invalid filename'}, status=400)
        
    backup_path = Path(settings.BASE_DIR) / 'backups' / filename
    
    if not backup_path.exists() or not backup_path.is_file():
        return JsonResponse({'error': 'Backup file not found'}, status=404)
        
    try:
        os.remove(backup_path)
        return JsonResponse({'success': True, 'message': 'Backup deleted successfully'})
    except Exception as e:
        return JsonResponse({'error': f'Failed to delete: {str(e)}'}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, review_id):
    """Delete a review permanently."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import Review
    review = get_object_or_404(Review, id=review_id)
    reviewer = review.reviewer_name
    review.delete()
    return JsonResponse({'message': f'Review by "{reviewer}" deleted successfully.'})


# --- SECTION 26: Sample Testimonials CRUD ---

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sample_testimonials_list(request):
    """List all sample testimonials."""
    from .models import SampleTestimonial
    samples = SampleTestimonial.objects.all()
    data = [{
        'id': s.id,
        'name': s.name,
        'text': s.text,
        'subtitle': s.subtitle,
        'rating': s.rating,
        'is_active': s.is_active,
    } for s in samples]
    return JsonResponse({'samples': data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sample_testimonial_create(request):
    """Create a new sample testimonial."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import SampleTestimonial
    data = json.loads(request.body)
    s = SampleTestimonial.objects.create(
        name=data.get('name', '').strip(),
        text=data.get('text', '').strip(),
        subtitle=data.get('subtitle', '').strip(),
        rating=int(data.get('rating', 5)),
        is_active=data.get('is_active', True),
    )
    return JsonResponse({'id': s.id, 'message': 'Sample testimonial created.'})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def sample_testimonial_update(request, sample_id):
    """Update a sample testimonial."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import SampleTestimonial
    s = get_object_or_404(SampleTestimonial, id=sample_id)
    data = json.loads(request.body)
    
    if 'name' in data: s.name = data['name'].strip()
    if 'text' in data: s.text = data['text'].strip()
    if 'subtitle' in data: s.subtitle = data['subtitle'].strip()
    if 'rating' in data: s.rating = int(data['rating'])
    if 'is_active' in data: s.is_active = data['is_active']
    s.save()
    return JsonResponse({'id': s.id, 'message': 'Updated successfully.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def sample_testimonial_delete(request, sample_id):
    """Delete a sample testimonial."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Admin only'}, status=403)
    
    from .models import SampleTestimonial
    s = get_object_or_404(SampleTestimonial, id=sample_id)
    s.delete()
    return JsonResponse({'message': 'Deleted successfully.'})