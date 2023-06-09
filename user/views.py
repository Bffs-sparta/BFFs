from .models import User, Profile, GuestBook, Verify

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
    def post(self, request):
        user_data = UserCreateSerializer(data=request.data)
        user_data.is_valid(raise_exception=True)
        user_data.save()
        return Response({"msg": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# 프로필 ru


class ProfileView(APIView):

    def get(self, request, user_id):
        profile = Profile.objects.get(id=user_id)

        serializer = UserProfileSerializer(profile)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, user_id):
        profile = Profile.objects.get(user_id=user_id)
        if profile.user == request.user:
            serializer = UserProfileUpdateSerializer(
                profile, data=request.data, partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "수정완료!"}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response({"message": "권한이 없습니다!"}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id):
        profile = User.objects.get(id=user_id)
        datas = request.data.copy()
        datas["is_active"] = False
        serializer = UserDelSerializer(profile, data=datas)
        if profile.check_password(request.data.get("password")):
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "계정 비활성화 완료"}, status=status.HTTP_204_NO_CONTENT
                )
        else:
            return Response(
                {"message": f"패스워드가 다릅니다"}, status=status.HTTP_400_BAD_REQUEST
            )


# 방명록 crud


class GuestBookView(APIView):
    def get(self, request, profile_id):
        profile = Profile.objects.get(id=profile_id)
        comments = profile.comment_set.all()
        serializer = GuestBookSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, profile_id):
        serializer = GuestBookCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, profile_id=profile_id)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GuestBookDetailView(APIView):
    def patch(self, request, profile_id, guestbook_id):
        comment = GuestBook.objects.get(id=guestbook_id)
        if request.user == comment.user:
            serializer = GuestBookCreateSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, profile_id, guestbook_id):
        comment = GuestBook.objects.get(id=guestbook_id)
        if request.user == comment.user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

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

