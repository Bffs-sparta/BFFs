from decouple import config
import requests

from django.contrib.auth.views import (
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from rest_framework.generics import get_object_or_404
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetConfirmView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User, Profile, GuestBook, Verify
from .serializers import (
    UserCreateSerializer,
    UserDelSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    GuestBookSerializer,
    GuestBookCreateSerializer,
)
from feed.serializers import FeedDetailSerializer
from community.models import CommunityAdmin
from community.serializers import CommunityCreateSerializer, MyCommunitySerializer
from .validators import email_validator
from .jwt_tokenserializer import CustomTokenObtainPairSerializer
from .tasks import verifymail, pwresetMail



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
        user = user_data.save()
        # user 생성될때 profile 생성
        return Response({"msg": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class NaverLoginView(APIView):
    def get(self, request):
        CLIENT_ID = config("NAVER_CLIENT_ID")
        STATE_STRING = get_random_string(16)
        CALLBACK_URL = config("BACKEND_URL") + "/user/naver/callback/"
        URL = f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={CLIENT_ID}&state={STATE_STRING}&redirect_uri={CALLBACK_URL}"
        return Response({"url": URL}, status=status.HTTP_200_OK)


class NaverCallbackView(APIView):
    def get(self, request):
        CLIENT_ID = config("NAVER_CLIENT_ID")
        CLIENT_SECRET = config("NAVER_CLIENT_SECRET")
        CODE = request.GET.get("code")
        STATE = request.GET.get("state")
        URL = f"https://nid.naver.com/oauth2.0/token?grant_type=authorization_code&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&code={CODE}&state={STATE}"
        response = requests.get(URL)
        response_json = response.json()
        access_token = response_json.get("access_token")

        TOKEN_URL = "https://openapi.naver.com/v1/nid/me"
        user_response = requests.get(
            TOKEN_URL, headers={"Authorization": "Bearer " + access_token}
        )
        user_response_json = user_response.json()
        user_data = user_response_json.get("response")
        email = user_data.get("email")
        name = user_data.get("name")
        profileimage = user_data.get("profile_image_url")
        social = "naver"
        return socialLogin(name=name, email=email, login_type=social)


class GoogleLoginView(APIView):
    def get(self, request):
        CLIENT_ID = config("KAKAO_CLIENT_ID")
        BACKEND_URL = config("BACKEND_URL")
        CALLBACK_URL = BACKEND_URL + "/user/google/callback/"
        URL = "https://accounts.google.com/o/oauth2/v2/auth"
        return Response(
            {"url": URL, "redirecturi": CALLBACK_URL, "client_id": CLIENT_ID},
            status=status.HTTP_200_OK,
        )


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        pass


class KakaoLoginView(APIView):
    def get(self, request):
        CLIENT_ID = config("KAKAO_CLIENT_ID")
        BACKEND_URL = config("BACKEND_URL")
        CALLBACK_URL = BACKEND_URL + "/user/kakao/callback/"
        URL = f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={CALLBACK_URL}&response_type=code"
        return Response(
            {"url": URL},
            status=status.HTTP_200_OK,
        )


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")  # url에서 code부분만 가져옴
        data = {
            "grant_type": "authorization_code",
            "client_id": config("KAKAO_CLIENT_ID"),
            "redirect_uri": config("BACKEND_URL") + "/user/kakao/callback/",
            "code": code,
            "client_secret": config("KAKAO_CLIENT_SECRET"),
        }
        access_token_request = requests.post(
            "https://kauth.kakao.com/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
            data=data,
        )
        token_data = access_token_request.json()
        access_token = token_data.get("access_token")
        user_data_response = requests.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_data = user_data_response.json()
        kakao_account = user_data.get("kakao_account")
        profile = kakao_account.get("profile")

        name = profile.get("nickname")
        email = kakao_account.get("email")
        social = "kakao"

        profile_image = profile.get("profile_image_url")
        age_range = kakao_account.get("age_range")
        return socialLogin(name=name, email=email, login_type=social)


def socialLogin(**kwargs):
    if User.objects.filter(email=kwargs.get("email")).exists():
        user = User.objects.get(email=kwargs.get("email"))
        if user.login_type != kwargs.get("login_type"):
            return Response(
                {"error": "선택한 소셜계정 외 다른 가입방법으로 가입된 이메일입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            return get_token(user)
    else:
        user = User.objects.create_user(**kwargs)
        user.set_unusable_password()
        user.save()
        return get_token(user)


def get_token(user):
    token = CustomTokenObtainPairSerializer.social_token(user)
    callback_url = f"{config('FRONTEND_URL')}/callback?access_token={token.get('access')}&refresh_token={token.get('refresh')}"
    return redirect(callback_url)

# 프로필 ru


# 프로필 id 받아오는 거로 수정할 예정!!!!!!!!!!!!!!!!!!
class ProfileView(APIView):
    def get(self, request, user_id):
        profile = Profile.objects.get(user_id=user_id)
        profile_serializer = UserProfileSerializer(profile)
        user = User.objects.get(id=user_id)
        bookmark = user.bookmark.all()
        bookmark_serializer = CommunityCreateSerializer(bookmark, many=True)
        community = CommunityAdmin.objects.filter(user_id=user_id)
        community_serializer = MyCommunitySerializer(community, many=True)
        feed = user.author.all()
        feed_serializer = FeedDetailSerializer(feed, many=True)
        return Response(
            {
                "profile": profile_serializer.data,
                "bookmark": bookmark_serializer.data,
                "community": community_serializer.data,
                "feed": feed_serializer.data,
            },
            status=status.HTTP_200_OK,
        )

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
        datas["is_withdraw"] = True
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

class MyPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = get_object_or_404(User, email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = request.build_absolute_uri(
            reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )
        pwresetMail.delay(email, reset_url)
        return Response({"detail": "비밀번호 변경 메일 발송!"})


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    success_url = "/user/password/reset/complete/"
    title = "비밀번호 초기화"


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"
    title = "비밀번호 초기화 완료"
