from rest_framework import serializers
from decouple import config

from user.models import User
from feed.models import Feed
from feed.serializers import FeedTitleSerializer
from .models import Community, CommunityAdmin, ForbiddenWord


class CommunitySerializer(serializers.ModelSerializer):
    imageurl = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    forbiddenword = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    feeds = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "introduction",
            "image",
            "imageurl",
            "is_approval",
            "bookmarked",
            "forbiddenword",
            "categories",
            "feeds",
            "admin",
        ]

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.image)

    def get_bookmarked(self, obj):
        return obj.bookmarked.count()

    def get_forbiddenword(self, obj):
        words = obj.forbiddenword.all()
        return [forbidden.word for forbidden in words]

    def get_categories(self, obj):
        categories = obj.community_category.all()
        category_name_list = [
            [category.id, category.category_name] for category in categories
        ]
        return category_name_list

    def get_feeds(self, obj):
        feeds = Feed.objects.filter(category__community=obj)
        feed = FeedTitleSerializer(feeds, many=True)
        return feed.data

    def get_admin(self, obj):
        admin = CommunityAdmin.objects.filter(community=obj)
        admin_serializer = CommunityAdminSerializer(admin, many=True)
        return admin_serializer.data


class CommunityCategorySerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "categories",
        ]

    def get_categories(self, obj):
        categories = obj.community_category.all()
        category_name_list = [
            [category.id, category.category_name] for category in categories
        ]
        return category_name_list


class CommunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = "__all__"


class CommunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = [
            "introduction",
            "image",
        ]


class CommunityAdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityAdmin
        fields = [
            "user",
        ]


class MyCommunitySerializer(serializers.ModelSerializer):
    title = serializers.StringRelatedField(source="community.title")
    introduction = serializers.StringRelatedField(source="community.introduction")
    image = serializers.StringRelatedField(source="community.image")

    class Meta:
        model = CommunityAdmin
        fields = [
            "user",
            "title",
            "introduction",
            "image",
        ]


class CommunityAdminSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source="user.email")
    name = serializers.StringRelatedField(source="user.name")
    nickname = serializers.StringRelatedField(source="user.nickname")
    last_login = serializers.StringRelatedField(source="user.last_login")

    class Meta:
        model = CommunityAdmin
        fields = [
            "user_id",
            "user",
            "name",
            "nickname",
            "is_comuadmin",
            "is_subadmin",
            "last_login",
        ]


class ForbiddenWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenWord
        fields = [
            "word",
        ]


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
