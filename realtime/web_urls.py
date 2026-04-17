from django.urls import path
from . import web_views

urlpatterns = [
    path('', web_views.home_view, name='home'),
    path('admin-dashboard/', web_views.admin_dashboard_view, name='admin-dashboard'),
]