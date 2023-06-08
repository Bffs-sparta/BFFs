from rest_framework import serializers
from .models import User, Verify
from rest_framework.generics import get_object_or_404


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
