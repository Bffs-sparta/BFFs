from rest_framework import serializers
from .models import AiChatBot


class AiChatBotSerailizer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()

    class Meta:
        model = AiChatBot
        fields = "__all__"

    def get_user(self, obj):
        return obj.user.id

    def get_username(self, obj):
        return obj.user.name
