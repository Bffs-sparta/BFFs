from .models import User, Profile, GuestBook, Verify

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
from .jwt_tokenserializer import CustomTokenObtainPairSerializer

from user.serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserDelSerializer,
    GuestBookSerializer,
    GuestBookCreateSerializer,
)

from .models import User, Profile


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

                # 테스트용
                return Response({"code": code}, status=status.HTTP_200_OK)
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
    def post(self, request):
        user_data = UserCreateSerializer(data=request.data)
        user_data.is_valid(raise_exception=True)
        user_data.save()
        return Response({"msg": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 프로필 ru


class ProfileView(APIView):
    # def get_object(self, user_id):
    #     return get_object_or_404(User, id=user_id)

    def get(self, request, user_id):
        # user = User.objects.get(id=user_id)
        # serializer = UserSerializer(user)
        # print(f'"⭐️", {serializer.data}')
        # return Response(serializer.data, status=status.HTTP_200_OK)
        profile = Profile.objects.get(id=user_id)
        print(f'"⭐️", {profile}')
        serializer = UserProfileSerializer(profile)
        print(f'"⭐️", {serializer.data}')
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        profile = Profile.objects.get(user_id=user_id)
        # print(f'"⭐️⭐️", {profile.user}')
        # me = request.user
        # print(f'"⭐️⭐️⭐️", {me}')
        if profile.user == request.user:
            serializer = UserProfileUpdateSerializer(
                profile, data=request.data, partial=True
            )
            print(f'"⭐️", {serializer}')
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)
