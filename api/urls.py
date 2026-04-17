from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Авторизація
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.UserLoginView.as_view(), name='login'),
    path('auth/profile/', views.UserProfileView.as_view(), name='profile'),

    # Оголошення та реакції
    path('announcements/', views.AnnouncementListView.as_view(), name='announcement-list'),
    path('announcements/<int:pk>/', views.AnnouncementDetailView.as_view(), name='announcement-detail'),
    path('reactions/toggle/', views.ToggleReactionView.as_view(), name='reaction-toggle'),

    # App info
    path('info/', views.app_info_view, name='app-info'),
]