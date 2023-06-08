from .models import User, Verify

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *
from threading import Timer
from .validators import email_validator
import requests
import os
from decouple import config


class SendEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @classmethod
    def timer_delet(*input_string):
        try:
            target = input_string[1]
            email_list = Verify.objects.filter(email=target)
            email_list.delete()
        except:
            pass

    def post(self, request):
        email = request.data.get("email", None)
        if email is None:
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
                subject = "BFFs 이메일 인증코드 메일입니다."
                from_email = config("EMAIL")
                code = get_random_string(length=6)
                if Verify.objects.filter(email=email).exists():
                    email_list = Verify.objects.filter(email=email)
                    email_list.delete()
                html_content = render_to_string("verfication.html", {"code": code})
                send_email = EmailMessage(subject, html_content, from_email, [email])
                send_email.content_subtype = "html"
                send_email.send()
                Verify.objects.create(email=email, code=code)

                timer = 600
                Timer(timer, self.timer_delet, (email,)).start()  # 테스트코드에서 있으면 10분동안 멈춤

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
                    {"error": "인증 코드가 틀렸습니다"}, status=status.HTTP_400_BAD_REQUEST
                )


class SignupView(APIView):
    def post(slef, request):
        user_data = UserCreateSerializer(data=request.data)
        user_data.is_valid(raise_exception=True)
        user_data.save()
        return Response({"msg": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
