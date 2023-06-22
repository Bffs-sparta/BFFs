from django.db import models
from django.conf import settings


class AiChatBot(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_text = models.JSONField(encoder=None, default=dict)
    ai_text = models.JSONField(encoder=None, default=dict)
