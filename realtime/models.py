from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class OnlineUser(models.Model):
    """Модель для відстеження онлайн користувачів"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='online_status'
    )
    channel_name = models.CharField(max_length=100, unique=True)
    connected_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    page_url = models.CharField(max_length=500, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    class Meta:
        verbose_name = 'Онлайн користувач'
        verbose_name_plural = 'Онлайн користувачі'
    
    def __str__(self):
        return f"{self.user.username} - {self.connected_at}"
    
    @classmethod
    def get_online_users(cls):
        """Отримати список онлайн користувачів"""
        # Користувачі активні протягом останніх 5 хвилин
        cutoff_time = timezone.now() - timedelta(minutes=5)
        return cls.objects.filter(last_activity__gte=cutoff_time).select_related('user')
    
    @classmethod
    def get_online_count(cls):
        """Кількість онлайн користувачів"""
        cutoff_time = timezone.now() - timedelta(minutes=5)
        return cls.objects.filter(last_activity__gte=cutoff_time).count()

class UserActivity(models.Model):
    """Модель для логування активності користувачів"""
    ACTIVITY_TYPES = [
        ('login', 'Вхід'),
        ('logout', 'Вихід'),
        ('announcement_view', 'Перегляд оголошення'),
        ('reaction_add', 'Додавання реакції'),
        ('reaction_change', 'Зміна реакції'),
        ('reaction_remove', 'Видалення реакції'),
        ('page_visit', 'Відвідування сторінки'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='activities'
        )
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Активність користувача'
        verbose_name_plural = 'Активність користувачів'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class RealtimeNotification(models.Model):
    """Модель для real-time сповіщень"""
    NOTIFICATION_TYPES = [
        ('new_announcement', 'Нове оголошення'),
        ('new_reaction', 'Нова реакція на оголошення'),
        ('system', 'Системне повідомлення'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
        )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_notifications',
        null=True, 
        blank=True
        )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"