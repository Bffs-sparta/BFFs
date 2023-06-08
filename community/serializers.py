from rest_framework import serializers
from .models import Community, CommunityAdmin, ForbiddenWord


class CommunitySerializer(serializers.ModelSerializer):
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ["id", "title", "introduction", "is_approval", "admin",]

    def get_admin(self, obj):        
        admin = CommunityAdmin.objects.filter(community=obj)
        admin_serializer = CommunityAdminerializer(admin, many=True)
        return admin_serializer.data


class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"


class CommunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = ["introduction",]


class CommunityAdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityAdmin
        fields = ["user",]


class CommunityAdminerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = CommunityAdmin
        fields = ["user", "is_comuadmin", "is_subadmin",]


class ForbiddenWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenWord
        fields = ["word",]