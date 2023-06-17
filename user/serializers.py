from rest_framework import serializers
from .models import User, Profile, GuestBook

from user.validators import (
    nickname_validator,
)
from django.utils import timezone
from django.core.files.storage import default_storage
from uuid import uuid4
import os
from decouple import config


# class UserCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         fields = ("email", "name", "password")
#         extra_kwargs = {"password": {"write_only": True}}
#         model = User

#     def create(self, validated_data):
#         verify = get_object_or_404(Verify, email=validated_data["email"])
#         if verify:
#             user = User.objects.create_user(**validated_data)
#             return user
#         else:
#             raise serializers.ValidationError("이메일 인증을 완료 해주세요")


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("email", "name", "password")
        extra_kwargs = {"password": {"write_only": True}}
        model = User

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    # 이메일,

    class Meta:
        model = Profile
        fields = (
            "user_email",
            "user_name",
            "nickname",
            "region",
            "introduction",
            "profileimage",
        )

    def get_user_name(self, obj):
        return obj.user.name

    def get_user_email(self, obj):
        return obj.user.email


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user_email",
            "nickname",
            "region",
            "introduction",
            "profileimage",
        )
        extra_kwargs = {
            "nickname": {
                "error_messages": {
                    "required": "닉네임을 입력해주세요.",
                    "blank": "닉네임을 입력해주세요.",
                }
            },
        }

    def get_user_email(self, obj):
        return obj.user.email

    def validate(self, data):
        nickname = data.get("nickname")

        # 닉네임 유효성 검사
        if nickname_validator(nickname):
            raise serializers.ValidationError(
                detail={"닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글,'-' 또는'_'만 사용 가능합니다."}
            )

        return data

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)

        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "name",
            "password",
        )
        extra_kwargs = {"password": {"write_only": True}}


class UserProfileSerializer(serializers.ModelSerializer):
    profileimageurl = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    # 이메일,

    class Meta:
        model = Profile
        fields = (
            "user_email",
            "user_name",
            "nickname",
            "region",
            "introduction",
            "profileimage",
            "profileimageurl",
            "created_at",
        )

    def get_profileimageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.profileimage)

    def get_user_name(self, obj):
        return obj.user.name

    def get_user_email(self, obj):
        return obj.user.email


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user_email",
            "nickname",
            "region",
            "introduction",
            "profileimage",
        )
        extra_kwargs = {
            "nickname": {
                "error_messages": {
                    "required": "닉네임을 입력해주세요.",
                    "blank": "닉네임을 입력해주세요.",
                }
            },
        }

    def get_user_email(self, obj):
        return obj.user.email

    def validate(self, data):
        nickname = data.get("nickname")

        # 닉네임 유효성 검사
        if nickname_validator(nickname):
            raise serializers.ValidationError(
                detail={"닉네임은 공백 없이 2자이상 8자 이하의 영문, 한글,'-' 또는'_'만 사용 가능합니다."}
            )

        return data

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        self.pre_delete_img(instance, validated_data)
        self.save_new_img(instance, validated_data)

        user.save()
        return user, instance

    def pre_delete_img(self, instance, validated_data):
        new_img = validated_data.get("profileimage")
        if new_img and instance.profileimage and new_img != instance.profileimage:
            try:
                default_storage.delete(instance.profileimage.path)
            except:
                pass

    def save_new_img(self, instance, validated_data):
        new_file = validated_data.get("profileimage")

        if new_file:
            ext = os.path.splitext(new_file.name)[-1]
            new_file_name = f"{uuid4().hex}{ext}"

            instance.profileimage = new_file
            instance.profileimage.name = new_file_name


class UserDelSerializer(serializers.ModelSerializer):
    user_password = serializers.SerializerMethodField()

    class Meta:
        model = User

        fields = ("is_withdraw", "user_password")

    def get_user_password(self, obj):
        return obj.user.password

    def withdraw(self):
        self.is_withdraw = False
        self.withdraw_at = timezone.now()
        self.save()


class GuestBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBook
        fields = "__all__"


class GuestBookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestBook
        fields = ("comment",)


class SearchUserSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="user.name")
    nickname = serializers.StringRelatedField(source="user.nickname")
    last_login = serializers.StringRelatedField(source="user.last_login")

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "nickname",
            "last_login",
        ]
