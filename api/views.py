from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from announcements.models import Announcement
from reactions.models import Reaction
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    AnnouncementSerializer, ReactionSerializer
)
from django.db.models import Count, Q
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class UserRegistrationView(generics.CreateAPIView):
    """
    Реєстрація нового користувача в системі.

    Створює новий акаунт користувача з обов'язковими полями:
    - email (унікальний)
    - username
    - first_name
    - last_name
    - password

    Опціональні поля:
    - gender
    - birth_date
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    Вхід користувача в систему.

    Очікує обов'язкові поля:
    - email
    - password

    При успішній перевірці повертає профіль користувача та токен доступу.
    Якщо облікові дані невірні або акаунт деактивовано, повертає помилку валідації з відповідним повідомленням.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Перегляд та редагування профілю користувача.

    - Повертає інформацію про профіль поточного авторизованого користувача.
    - Оновлює особисті дані.

    Доступ дозволено виключно авторизованим користувачам.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AnnouncementListView(generics.ListCreateAPIView):
    """
    Отримання списку оголошень та публікація нових.

    - Повертає список всіх активних оголошень.
    - Створює нове оголошення. Доступно тільки адміністраторам.

    Підтримує сортування та фільтрацію.
    """
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    ordering_fields = ['created_at', 'views_count', 'likes_count', 'fire_count', 'heart_count', 'sad_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Announcement.objects.filter(is_active=True).annotate(
            likes_count=Count('reactions', filter=Q(reactions__reaction_type='like'), distinct=True),
            fire_count=Count('reactions', filter=Q(reactions__reaction_type='fire'), distinct=True),
            heart_count=Count('reactions', filter=Q(reactions__reaction_type='heart'), distinct=True),
            sad_count=Count('reactions', filter=Q(reactions__reaction_type='sad'), distinct=True),
        ).prefetch_related('reactions')

        has_reaction = self.request.query_params.get('has_reaction')
        if has_reaction in ['like', 'fire', 'heart', 'sad']:
            queryset = queryset.filter(reactions__reaction_type=has_reaction).distinct()

        min_likes = self.request.query_params.get('min_likes')
        if min_likes is not None and min_likes.isdigit():
            queryset = queryset.filter(likes_count__gte=int(min_likes))

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детальний перегляд, редагування або видалення конкретного оголошення.

    - Повертає деталі оголошення за його ID.
      При кожному запиті лічильник переглядів автоматично збільшується на 1.
    - Редагує існуюче оголошення. Доступно тільки адміністраторам.
    - Видаляє оголошення. Доступно тільки адміністраторам.
    """
    queryset = Announcement.objects.filter(is_active=True)
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAdminOrReadOnly]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ToggleReactionView(generics.CreateAPIView):
    """
    Встановлення, зміна або видалення реакції на оголошення.

    Тіло запиту:
    - announcement: ID оголошення
    - reaction_type: тип реакції (наприклад: 'like', 'heart', 'fire', 'sad')

    Поведінка:
    - Якщо користувач ще не залишав реакцію: створює нову.
    - Якщо користувач натискає на іншу реакцію: оновлює існуючу.
    - Якщо користувач натискає на ту ж саму реакцію ще раз: видаляє її.
    """
    serializer_class = ReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        announcement_id = request.data.get('announcement')
        reaction_type = request.data.get('reaction_type')

        reaction, created = Reaction.objects.get_or_create(
            announcement_id=announcement_id,
            user=request.user,
            defaults={'reaction_type': reaction_type}
        )

        if not created and reaction.reaction_type != reaction_type:
            reaction.reaction_type = reaction_type
            reaction.save()
            msg = f"Реакцію змінено на {reaction_type}"
            status_code = status.HTTP_200_OK

        elif not created and reaction.reaction_type == reaction_type:
            reaction.delete()
            return Response({"message": "Реакцію видалено"}, status=status.HTTP_204_NO_CONTENT)

        else:
            msg = "Реакцію додано"
            status_code = status.HTTP_201_CREATED

        return Response({"message": msg, "reaction_type": reaction.reaction_type}, status=status_code)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def app_info_view(request):
    """
    Отримання загальної інформації про додаток.
    """
    return Response({
        'name': 'Канал Оголошень',
        'version': '1.0.0',
        'description': 'Канал оголошень, де адміністратор створює пости, а користувачі можуть залишати реакції.',
        'features': [
            'Реєстрація та авторизація користувачів',
            'Перегляд стрічки оголошень',
            'Створення оголошень адміністратором',
            'Система реакцій (лайки, вогонь, серце тощо)'
        ],
        'author': '1i',
        'contact': '@Joe_1i'
    })