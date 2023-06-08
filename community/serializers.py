from rest_framework import serializers

from user.models import User
from .models import Community, CommunityAdmin, ForbiddenWord


class CommunitySerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "introduction",
            "is_approval",
            "admin",
        ]

    def get_admin(self, obj):
        admin = CommunityAdmin.objects.filter(community=obj)
        admin_serializer = CommunityAdminSerializer(admin, many=True)
        return admin_serializer.data


class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"


class CommunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = [
            "introduction",
        ]


class CommunityAdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityAdmin
        fields = [
            "user",
        ]


class CommunityAdminSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = CommunityAdmin
        fields = [
            "user",
            "is_comuadmin",
            "is_subadmin",
        ]


class ForbiddenWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenWord
        fields = [
            "word",
        ]


class SearchUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "name",
        ]
