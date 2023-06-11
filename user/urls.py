from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupView,
    LoginView,
    KakaoLoginView,
    KakaoCallbackView,
    SendEmailView,
    VerificationEmailView,
    ProfileView,
    GuestBookView,
    GuestBookDetailView,
    MyPasswordResetView,
    MyPasswordResetDoneView,
    MyPasswordResetConfirmView,
    MyPasswordResetCompleteView,
    NaverLoginView,
    NaverCallbackView,
    GoogleLoginView,
    GoogleCallbackView,
)

urlpatterns = [
    path("", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("kakao/login/", KakaoLoginView.as_view(), name="kakao_login"),
    path("kakao/callback/", KakaoCallbackView.as_view(), name="kakao_login"),
    path("email/", SendEmailView.as_view(), name="email"),
    path("email/verify/", VerificationEmailView.as_view(), name="verify"),
    path("<int:user_id>/", ProfileView.as_view(), name="profile_view"),
    path(
        "<int:profile_id>/guestbook/",
        GuestBookView.as_view(),
        name="guestbook_view",
    ),
    path(
        "<int:profile_id>/guestbook/<int:guestbook_id>/",
        GuestBookDetailView.as_view(),
        name="guestbook_detail_view",
    ),
    path("password/reset/", MyPasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/done/",
        MyPasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        MyPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        MyPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    path("naver/login/", NaverLoginView.as_view(), name="naver_login"),
    path("naver/callback/", NaverCallbackView.as_view(), name="naver_callback"),
    path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google_callback"),
]
