"""
Section 7: Public AI Chatbot using Groq (llama3-8b-8192)
Section 8: Admin Business Chatbot (ORM-based insights)

Endpoints:
- POST /api/chatbot/       → Public chatbot (menu, booking info)
- POST /api/admin-chat/    → Admin business insights chatbot
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json


def _get_groq_client():
    """Get Groq client if API key is configured."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None
    try:
        # pyrefly: ignore [missing-import]
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None


# =========================================
# SECTION 7: Public Chatbot
# =========================================
PUBLIC_SYSTEM_PROMPT = """You are "Swagat Assistant", the exclusive AI concierge for Swagat Caterers — a premium, highly-rated catering service based in Rajkot, Gujarat, India.

Your Persona:
- You are exceptionally warm, hospitable, and professional, embodying the spirit of "Atithi Devo Bhava" (The guest is God).
- You speak with an elegant, inviting, and mouth-watering tone when describing food.
- You are highly organized. You MUST use bullet points and emojis to make your answers easy to read and visually appealing.

Key Information:
- We specialize in authentic Gujarati, Kathiyawadi, Punjabi, and Jain vegetarian cuisine for weddings, corporate events, and grand celebrations.
- Services: Premium full catering, interactive live counters, exquisite starters, rich desserts, elegant beverage stations, and beautiful dining decoration.
- We serve across Gujarat and nearby states.
- Our menus are fully customizable based on guest count, budget, and specific dietary needs (e.g., strict Jain food prepared in separate utensils).

Popular Menu Highlights (Describe them deliciously if asked):
- Gujarati/Kathiyawadi: Authentic Undhiyu, Spiced Handvo, Soft Dhokla, Dal Dhokli, Farsan.
- Punjabi: Creamy Dal Makhani, Rich Paneer Tikka Masala, Aromatic Veg Biryani.
- Desserts: Melt-in-mouth Gulab Jamun, Crispy Hot Jalebi, Premium Shrikhand.

Response Guidelines:
- Format your replies beautifully using emojis (🍲, ✨, 📅, etc.) and short bullet points.
- Keep responses engaging but concise (under 100 words if possible).
- If asked about pricing, kindly explain: "Pricing is highly customized based on your specific menu choices and guest count. 📅 Let's book a consultation to give you an exact quote!"
- If asked to see the menu or view menu options, always provide this exact link: [Click here to view our Full Menu](/menu/)
- Never sound robotic. Never mention you are an AI unless directly asked.
- Always end with a polite, helpful closing question (e.g., "What kind of event are you planning?")."""


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def public_chatbot(request):
    """Public AI chatbot endpoint using Groq."""
    user_message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not user_message:
        return Response({'error': 'Message is required'}, status=400)

    client = _get_groq_client()
    if not client:
        return Response({
            'reply': "🙏 Welcome to Swagat Caterers! We'd love to help you plan your perfect event. "
                     "Please call us or visit our booking page to get started!",
            'source': 'fallback'
        })

    try:
        # Build message history
        messages = [{'role': 'system', 'content': PUBLIC_SYSTEM_PROMPT}]
        
        # Add conversation history (last 6 messages)
        for msg in history[-6:]:
            messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })
        
        messages.append({'role': 'user', 'content': user_message})

        completion = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=messages,
            temperature=0.7,
            max_tokens=300,
        )

        reply = completion.choices[0].message.content
        return Response({'reply': reply, 'source': 'groq'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Groq Chatbot Error: {e}")
        return Response({
            'reply': "I'm having trouble connecting right now. Please try again or contact us directly!",
            'source': 'error',
            'detail': str(e)
        })


# =========================================
# SECTION 8: Admin Business Chatbot
# =========================================
ADMIN_SYSTEM_PROMPT = """You are a business analytics assistant for Swagat Caterers admin dashboard.

You help analyze catering business data. When the user asks questions, you will be given actual data from the database.

Your job is to:
1. Analyze the data provided
2. Give clear, actionable insights
3. Use numbers and percentages
4. Be concise and professional

If no data is provided, explain what data would be needed to answer the question."""


def _get_business_context():
    """Fetch business data from ORM for admin chatbot context."""
    from .models import CateringEvent, Member, Booking, Menu_item, TaskAssignment
    from django.db.models import Sum, Count, Avg
    from django.utils import timezone
    from datetime import timedelta

    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    try:
        context = {
            'total_events': CateringEvent.objects.count(),
            'upcoming_events': CateringEvent.objects.filter(
                date__gte=now.date()
            ).count(),
            'events_this_month': CateringEvent.objects.filter(
                date__month=now.month, date__year=now.year
            ).count(),
            'status_breakdown': dict(
                CateringEvent.objects.values_list('status')
                    .annotate(count=Count('id'))
                    .values_list('status', 'count')
            ),
            'total_bookings': Booking.objects.count(),
            'recent_bookings': Booking.objects.filter(
                created_at__gte=thirty_days_ago
            ).count(),
            'total_staff': Member.objects.count(),
            'total_menu_items': Menu_item.objects.count(),
            'avg_guests': CateringEvent.objects.aggregate(
                avg=Avg('guests')
            )['avg'] or 0,
            'revenue_info': CateringEvent.objects.aggregate(
                total_advance=Sum('advance_amount')
            ),
            'popular_event_types': list(
                CateringEvent.objects.values('event_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:5]
            ),
            'pending_tasks': TaskAssignment.objects.filter(
                status='pending'
            ).count() if TaskAssignment.objects.exists() else 0,
        }
        return json.dumps(context, indent=2, default=str)
    except Exception as e:
        return f"Error fetching data: {e}"


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_chatbot(request):
    """Admin business chatbot endpoint using Groq + ORM data."""
    user_type = getattr(request.user, 'user_type', 'customer')
    if user_type not in ('admin', 'manager'):
        return Response({'error': 'Permission denied'}, status=403)

    user_message = request.data.get('message', '').strip()
    history = request.data.get('history', [])

    if not user_message:
        return Response({'error': 'Message is required'}, status=400)

    # Fetch business context
    business_data = _get_business_context()

    client = _get_groq_client()
    if not client:
        return Response({
            'reply': f"📊 Here's the current business data:\n\n{business_data}\n\n"
                     "Groq AI is not configured. Set GROQ_API_KEY for intelligent analysis.",
            'source': 'data_only'
        })

    try:
        messages = [
            {'role': 'system', 'content': ADMIN_SYSTEM_PROMPT},
            {'role': 'system', 'content': f'Current business data:\n{business_data}'},
        ]

        for msg in history[-6:]:
            messages.append({
                'role': msg.get('role', 'user'),
                'content': msg.get('content', '')
            })

        messages.append({'role': 'user', 'content': user_message})

        completion = client.chat.completions.create(
            model='llama-3.1-8b-instant',
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )

        reply = completion.choices[0].message.content
        return Response({'reply': reply, 'source': 'groq'})

    except Exception as e:
        return Response({
            'reply': f"Analysis error. Here's the raw data:\n\n{business_data}",
            'source': 'error',
            'detail': str(e)
        })
