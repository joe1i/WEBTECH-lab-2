from django.db import models
from django.conf import settings


class Announcement(models.Model):
    """Модель оголошення в каналі"""

    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Текст оголошення')
    image = models.ImageField(upload_to='announcements/', null=True, blank=True, verbose_name='Зображення')

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name='Адміністратор'
    )

    views_count = models.PositiveIntegerField(default=0, verbose_name='Кількість переглядів')
    is_active = models.BooleanField(default=True, verbose_name='Активне')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публікації')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата оновлення')

    class Meta:
        verbose_name = 'Оголошення'
        verbose_name_plural = 'Оголошення'
        ordering = ['-created_at']

    def __str__(self):
        return self.title