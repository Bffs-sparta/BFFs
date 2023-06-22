from django.urls import path
from .views import SendTextView

urlpatterns = [
    path("", SendTextView.as_view(), name="send_text_view"),
]
