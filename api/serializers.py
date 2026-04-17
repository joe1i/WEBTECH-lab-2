from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from announcements.models import Announcement
from reactions.models import Reaction

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Серіалізатор для реєстрації користувача"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'gender', 'birth_date', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Паролі не співпадають")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Серіалізатор для входу користувача"""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError('Невірний email або пароль')
            if not user.is_active:
                raise serializers.ValidationError('Акаунт деактивовано')
            data['user'] = user
        else:
            raise serializers.ValidationError('Необхідно вказати email та пароль')
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Серіалізатор для профілю користувача"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'first_name', 'last_name', 'gender', 'birth_date', 'avatar', 'bio',
                  'created_at']
        read_only_fields = ['id', 'email', 'created_at']


class ReactionSerializer(serializers.ModelSerializer):
    """Серіалізатор для відправки реакції"""

    class Meta:
        model = Reaction
        fields = ['announcement', 'reaction_type']


class AnnouncementSerializer(serializers.ModelSerializer):
    """Серіалізатор для оголошень"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    author_avatar = serializers.ImageField(source='author.avatar', read_only=True)
    reactions_summary = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'content', 'image', 'author_username', 'author_name', 'author_avatar',
            'views_count', 'created_at', 'reactions_summary', 'user_reaction'
        ]
        read_only_fields = ['id', 'views_count', 'created_at', 'author_name']

    def get_reactions_summary(self, obj):
        reactions = obj.reactions.all()
        return {
            'like': reactions.filter(reaction_type='like').count(),
            'heart': reactions.filter(reaction_type='heart').count(),
            'fire': reactions.filter(reaction_type='fire').count(),
            'sad': reactions.filter(reaction_type='sad').count(),
        }

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            reaction = obj.reactions.filter(user=request.user).first()
            if reaction:
                return reaction.reaction_type
        return None