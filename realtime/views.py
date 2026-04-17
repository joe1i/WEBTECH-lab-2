from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from datetime import timedelta
from .models import OnlineUser, UserActivity, RealtimeNotification
from .serializers import OnlineUserSerializer, UserActivitySerializer, RealtimeNotificationSerializer

class OnlineUsersListView(generics.ListAPIView):
    """Список онлайн користувачів"""
    serializer_class = OnlineUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return OnlineUser.get_online_users()

class UserActivityListView(generics.ListAPIView):
    """Список активності користувачів"""
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Показувати активність за останні 24 години
        since = timezone.now() - timedelta(hours=24)

        if self.request.user.is_staff:
            # Адміністратори бачать всю активність
            return UserActivity.objects.filter(created_at__gte=since).select_related('user').order_by('-created_at')
        else:
            # Звичайні користувачі бачать тільки свою активність
            return UserActivity.objects.filter(
                user=self.request.user,
                created_at__gte=since
            )

class NotificationListView(generics.ListAPIView):
    """Список сповіщень користувача"""
    serializer_class = RealtimeNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RealtimeNotification.objects.filter(
            recipient=self.request.user
        ).select_related('sender').order_by('-created_at')

class MarkNotificationReadView(generics.UpdateAPIView):
    """Позначити сповіщення як прочитане"""
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, notification_id):
        try:
            notification = RealtimeNotification.objects.get(
                id=notification_id,
                recipient=request.user
            )
            notification.is_read = True
            notification.save()
            
            return Response({'status': 'marked_as_read'})
        except RealtimeNotification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def online_stats_view(request):
    """Статистика для адмін-панелі"""
    online_count = OnlineUser.get_online_count()
    online_users = OnlineUser.get_online_users()
    
    # Статистика по сторінках
    page_stats = {}
    for user in online_users:
        if user.page_url:
            page_stats[user.page_url] = page_stats.get(user.page_url, 0) + 1
            
    return Response({
        'online_count': online_count,
        'page_statistics': page_stats,
        'is_admin': request.user.is_staff
    })