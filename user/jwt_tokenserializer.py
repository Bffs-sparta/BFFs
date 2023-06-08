from rest_framework import serializers
from .models import User
from rest_framework.generics import get_object_or_404
from rest_framework_simplejwt.serializers import (
    TokenObtainSerializer,
    update_last_login,
    authenticate,
    TokenObtainPairSerializer,
    RefreshToken,
)
from rest_framework_simplejwt.settings import api_settings
from datetime import timedelta
from django.utils import timezone


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    default_error_messages = {"no_active_account": "아이디나 비밀번호가 틀립니다"}
    token_class = RefreshToken

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["name"] = user.name
        return token

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            "password": attrs["password"],
        }
        try:
            authenticate_kwargs["request"] = self.context["request"]
        except KeyError:
            pass

        self.user = authenticate(**authenticate_kwargs)

        self.target = get_object_or_404(User, email=attrs[self.username_field])
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            if self.target:
                self.target.login_count += 1
                self.target.save()
            raise serializers.ValidationError(
                self.error_messages["no_active_account"],
                "no_active_account",
            )
        if self.target.banned_at and self.target.banned_at < timezone.now():
            self.target.banned_at = None
            self.target.login_count = 0
            self.target.save()

        if self.target.login_count > 5:
            self.target.banned_at = timezone.now() + timedelta(minutes=5)
            self.target.save()
            raise serializers.ValidationError("5회 이상 로그인 실패로 5분간 로그인이 불가능합니다")

        if self.target.is_withdraw:
            raise serializers.ValidationError("탈퇴한 회원입니다")
        elif self.target.is_dormant:
            raise serializers.ValidationError("휴면계정으로 전환된 회원입니다")

        refresh = self.get_token(self.user)

        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return {"access": attrs["access"], "refresh": attrs["refresh"]}
