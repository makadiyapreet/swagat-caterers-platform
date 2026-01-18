from multiprocessing.managers import Token
from django.shortcuts import get_object_or_404, HttpResponse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.signing import Signer, BadSignature
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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

domin = "https://swagat-caterers-platform-production.up.railway.app"
User = get_user_model()
signer = Signer()

# --- 1. ACTIVATION & APPROVAL VIEW ---
@csrf_exempt
def activate_user(request, token):
    try:
        user_id = signer.unsign(token)
        user = get_object_or_404(User, pk=user_id)
        
        if request.method == 'POST':
            if not user.is_active:
                selected_role = request.POST.get('role')
                user.user_type = selected_role
                user.is_active = True
                if selected_role in ['manager', 'admin']:
                    user.is_staff = True
                user.save() 
                return HttpResponse(f"<h1 style='color:green; text-align:center;'>Success! User {user.username} is active.</h1>")
            else:
                return HttpResponse(f"<h1 style='text-align:center;'>User {user.username} is already active.</h1>")

        return HttpResponse(f"""
            <html><body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                <h2>Approve User: {user.username}</h2>
                <form method="POST">
                    <select name="role" style="padding:10px;"><option value="customer">Customer</option><option value="manager">Manager</option><option value="admin">Admin</option></select>
                    <button type="submit" style="padding:10px; background:#D4AF37; color:white; border:none; cursor:pointer;">Approve</button>
                </form>
            </body></html>
        """)
            
    except BadSignature:
        return HttpResponse("<h1 style='color:red;'>Invalid Link</h1>", status=400)

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
                message=data.get('message')
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
                fail_silently=False,
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
            
            client_name = data.get('name')
            client_phone = data.get('phone')
            message_body = data.get('message')
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
                'swagatcaterersofficial@gmail.com',  # <--- SENDER (Must match settings.py EMAIL_HOST_USER)
                ['swagatcaterersofficial@gmail.com'], # <--- RECEIVER (Where you want the enquiry to go)
                fail_silently=False,
            )

            return JsonResponse({'status': 'success', 'message': 'Email sent successfully!'})

        except Exception as e:
            # Print the error to your console so you can see why it failed
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

# --- 9. ACTIVATION VIEW FOR FRONTEND ---   
def activate_user(request, token):
    try:
        # 1. Unsign the token
        user_id = signer.unsign(token, max_age=86400)
        
        # 2. Get the user directly from DB
        user = User.objects.get(pk=user_id)
        
        # 3. Activate
        if not user.is_active:
            user.is_active = True
            user.save() # This triggers the signal to send the Welcome Email
            return HttpResponse(f"<h1 style='color:green'>Success! User {user.username} activated.</h1>")
        else:
            return HttpResponse(f"<h1 style='color:orange'>User {user.username} is already active.</h1>")
            
    except BadSignature:
        return HttpResponse("Invalid or Expired Link", status=400)
    except User.DoesNotExist:
        return HttpResponse("User not found", status=404)
    
# --- 10. FRONTEND HOME VIEW ---
def frontend_home(request):
    return render(request, "index.html")

def index(request):
    return render(request, "index.html")

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