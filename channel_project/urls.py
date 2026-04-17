from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('api/', include('api.urls')),
    path('api/realtime/', include('realtime.urls')), 
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Static pages
    path('', include('realtime.web_urls')),  # Веб-сторінки

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)