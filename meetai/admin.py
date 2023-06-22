from django.contrib import admin
from meetai.models import AiChatBot


list_display = ["id", "user_id", "user_text", "ai_text"]

search_fields = ["user_id"]
ordering = ["user_id"]


admin.site.register(AiChatBot)
