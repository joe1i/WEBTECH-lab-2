from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from announcements.models import Announcement
from django.db.models import Count, Q
from reactions.models import Reaction
from .models import OnlineUser

User = get_user_model()

def home_view(request):
    """Головна сторінка"""
    recent_announcements = Announcement.objects.filter(is_active=True).annotate(
        like_count=Count('reactions', filter=Q(reactions__reaction_type='like')),
        heart_count=Count('reactions', filter=Q(reactions__reaction_type='heart')),
        fire_count=Count('reactions', filter=Q(reactions__reaction_type='fire')),
        sad_count=Count('reactions', filter=Q(reactions__reaction_type='sad')),
    ).order_by('-created_at')[:5]
    
    recent_reactions = Reaction.objects.all().order_by('-created_at')[:10]
    online_count = OnlineUser.get_online_count()
    
    context = {
        'recent_announcements': recent_announcements,
        'recent_reactions': recent_reactions,
        'online_count': online_count,
    }
    return render(request, 'realtime/home.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_dashboard_view(request):
    """Адміністративна панель для перегляду онлайн користувачів"""
    context = {
        'user': request.user,
    }
    return render(request, 'realtime/admin_dashboard.html', context)