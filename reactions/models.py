from django.db import models
from django.conf import settings
from announcements.models import Announcement


class Reaction(models.Model):
    """Модель реакції користувача на оголошення"""

    REACTION_CHOICES = [
        ('like', '👍 Лайк'),
        ('heart', '❤️ Серце'),
        ('fire', '🔥 Вогонь'),
        ('sad', '😢 Сумно'),
    ]

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='reactions',
        verbose_name='Оголошення'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Користувач'
    )
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES, verbose_name='Тип реакції')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата створення')

    class Meta:
        unique_together = ('announcement', 'user')
        verbose_name = 'Реакція'
        verbose_name_plural = 'Реакції'

    def __str__(self):
        return f"{self.user.email} -> {self.get_reaction_type_display()} на '{self.announcement.title}'"