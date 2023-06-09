from rest_framework import serializers
from .models import User, Profile, GuestBook, Verify
from rest_framework.generics import get_object_or_404
from .models import User, Profile, Verify
from user.validators import (
    nickname_validator,
)

from django.core.files.storage import default_storage
from uuid import uuid4
import os


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("email", "name", "password")
        extra_kwargs = {"password": {"write_only": True}}
        model = User

    def create(self, validated_data):
        # verify = get_object_or_404(Verify, email=validated_data['email'])
        # if verify:
        #     user = User.objects.create_user(**validated_data)
        #     return user
        # else:
        #     raise serializers.ValidationError("이메일 인증을 완료 해주세요")
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
