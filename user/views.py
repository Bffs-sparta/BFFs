from .models import User, Verify

from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from .validators import email_validator
import requests
import os
from decouple import config
from .jwt_tokenserializer import CustomTokenObtainPairSerializer
from django.utils.crypto import get_random_string
from .tasks import verifymail


class SendEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        if not email:
            return Response(
                {"error": "이메일을 작성해 주세요"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif not email_validator(email):
            return Response(
                {"error": "이메일 형식이 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            if User.objects.filter(email=email).exists():
                return Response(
                    {"error": "이미 가입한 회원입니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            else:
                if Verify.objects.filter(email=email).exists():
                    email_list = Verify.objects.filter(email=email)
                    email_list.delete()
                code = get_random_string(length=6)
                verifymail.delay(email, code)
                Verify.objects.create(email=email, code=code)

                return Response({"code": code}, status=status.HTTP_200_OK)  # 테스트용
                # return Response({'success':'success'},status=status.HTTP_200_OK)


class VerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "")
        code = request.data.get("code", "")
        if not email:
            return Response(
                {"error": "이메일이 입력이 안되어있습니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        elif not code:
            return Response(
                {"error": "인증 코드가 입력이 안되어있습니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            verify = Verify.objects.filter(email=email, code=code).first()
            if verify:
                verify.is_verify = True
                verify.save()
                return Response({"msg": "메일인증이 완료되었습니다"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "이메일이나 인증코드가 인증 코드가 틀렸습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class SignupView(APIView):
    def post(slef, request):
        user_data = UserCreateSerializer(data=request.data)
        user_data.is_valid(raise_exception=True)
        user_data.save()
        return Response({"msg": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MyPasswordResetView(PasswordResetView):
    html_email_template_name = "email.html"
    template_name = "password_reset_form.html"
    email_template_name = "email.html"
    subject_template_name = "email.txt"
    success_url = "done/"


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "password_reset_done.html"
    title = "비밀번호 문자 전송"


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    success_url = "/user/password/reset/complete/"
    title = "비밀번호 초기화"


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"
    title = "비밀번호 초기화 완료"
