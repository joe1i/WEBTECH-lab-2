from rest_framework import serializers
from .models import OnlineUser, UserActivity, RealtimeNotification

class OnlineUserSerializer(serializers.ModelSerializer):
    """Серіалізатор для онлайн користувачів"""
    user = serializers.StringRelatedField()
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = OnlineUser
        fields = ['user', 'username', 'full_name', 'connected_at', 'last_activity', 'page_url']

class UserActivitySerializer(serializers.ModelSerializer):
    """Серіалізатор для активності користувачів"""
    user = serializers.StringRelatedField()
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)

    class Meta:
        model = UserActivity
        fields = ['user', 'activity_type', 'activity_type_display', 'description', 'created_at']

class RealtimeNotificationSerializer(serializers.ModelSerializer):
    """Серіалізатор для сповіщень"""
    sender = serializers.StringRelatedField()
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)

    class Meta:
        model = RealtimeNotification
        fields = ['id', 'sender', 'notification_type', 'notification_type_display', 'title', 'message', 'data', 'is_read', 'created_at']