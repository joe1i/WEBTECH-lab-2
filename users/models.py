from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Розширена модель користувача"""

    GENDER_CHOICES = [
        ('M', 'Чоловіча'),
        ('F', 'Жіноча'),
        ('O', 'Інша'),
    ]

    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=30, verbose_name="Ім'я")
    last_name = models.CharField(max_length=30, verbose_name='Прізвище')
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name='Стать'
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name='Дата народження')
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='Біографія')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата реєстрації')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"