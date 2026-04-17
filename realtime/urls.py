from django.urls import path
from . import views

app_name = 'realtime'

urlpatterns = [
    path('online-users/', views.OnlineUsersListView.as_view(), name='online-users'),
    path('activity/', views.UserActivityListView.as_view(), name='user-activity'),
    path('notifications/', views.NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:notification_id>/read/', views.MarkNotificationReadView.as_view(), name='mark-read'),
    path('stats/', views.online_stats_view, name='online-stats'),
]