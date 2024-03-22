from django.contrib.auth.models import AbstractUser
from django.db import models


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True, db_index=True, verbose_name='Прошел активацию?')
    send_message = models.BooleanField(default=True, verbose_name='Присылать оповещения о новых комментах?')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
