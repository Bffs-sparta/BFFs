from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("email/", views.SendEmailView.as_view(), name="email"),
    path("email/verify/", views.VerificationEmailView.as_view(), name="verify"),
    path("<int:user_id>/", views.ProfileView.as_view(), name="profile_view"),
    path(
        "<int:profile_id>/guestbook/",
        views.GuestBookView.as_view(),
        name="guestbook_view",
    ),
    path(
        "<int:profile_id>/guestbook/<int:guestbook_id>/",
        views.GuestBookDetailView.as_view(),
        name="guestbook_detail_view",

    path("password/reset/", views.MyPasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/done/",
        views.MyPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.MyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views.MyPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
