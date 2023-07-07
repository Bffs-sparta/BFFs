import re
from rest_framework import serializers
from decouple import config

from user.models import User
from feed.models import Feed, Category, GroupPurchase
from feed.serializers import FeedListSerializer, FeedTitleSerializer
from .models import Community, CommunityAdmin, ForbiddenWord
from .validators import can_only_eng_int_underbar_and_hyphen


class CommunitySerializer(serializers.ModelSerializer):
    imageurl = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    forbiddenword = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    feeds = serializers.SerializerMethodField()
    admin = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "communityurl",
            "introduction",
            "image",
            "imageurl",
            "is_approval",
            "bookmarked",
            "is_bookmarked",
            "forbiddenword",
            "categories",
            "feeds",
            "admin",
        ]

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.image)

    def get_bookmarked(self, obj):
        return obj.bookmarked.count()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request.user and request.user.is_authenticated:
            return obj.bookmarked.filter(id=request.user.id).exists()
        return False

    def get_forbiddenword(self, obj):
        words = obj.forbiddenword.all()
        return [forbidden.word for forbidden in words]

    def get_categories(self, obj):
        categories = obj.community_category.all()
        category_name_list = [
            [category.id, category.category_name, category.category_url]
            for category in categories
        ]
        return category_name_list

    def get_feeds(self, obj):
        feeds = Feed.objects.filter(category__community=obj)
        feed = FeedListSerializer(feeds, many=True)
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
            [category.id, category.category_name, category.category_url]
            for category in categories
        ]
        return category_name_list


class CommunityCreateSerializer(serializers.ModelSerializer):
    imageurl = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "communityurl",
            "introduction",
            "image",
            "imageurl",
            "is_approval",
            "is_bookmarked",
        ]
        extra_kwargs = {
            "title": {
                "error_messages": {
                    "blank": "커뮤니티 이름을 입력해주세요.",
                    "min_length": "커뮤니티 이름은 2글자 이상 작성해주세요.",
                },
            },
            "communityurl": {"error_messages": {"blank": "커뮤니티 영어 이름을 입력해주세요."}},
            "introduction": {"error_messages": {"blank": "커뮤니티 소개를 입력해주세요."}},
        }

    def create(self, validated_data):
        title = validated_data.get("title")
        communityurl = validated_data.get("communityurl")
        if " " in title:
            raise serializers.ValidationError("커뮤니티 이름은 공백 없이 작성가능합니다.")
        if not re.match(r"^[a-zA-Z0-9가-힣]+$", title):
            raise serializers.ValidationError("커뮤니티 이름은 특수문자를 사용할 수 없습니다.")
        if " " in communityurl:
            raise serializers.ValidationError("커뮤니티 영어 이름은 공백 없이 작성가능합니다.")
        if Community.objects.filter(title=title).exists():
            raise serializers.ValidationError("이미 존재하는 커뮤니티 이름입니다.")
        if not can_only_eng_int_underbar_and_hyphen(communityurl):
            raise serializers.ValidationError(
                "커뮤니티 영어 이름은 영어와 숫자, 특수문자'-_' 포함 5글자 이상인 경우에 작성가능합니다."
            )
        if Community.objects.filter(title=title).exists():
            raise serializers.ValidationError("이미 존재하는 커뮤니티 이름입니다.")
        if Community.objects.filter(communityurl=communityurl).exists():
            raise serializers.ValidationError("이미 존재하는 커뮤니티 영어 이름입니다.")

        introduction = validated_data.get("introduction")
        image = validated_data.get("image")

        community = Community.objects.create(
            title=title,
            communityurl=communityurl,
            introduction=introduction,
            image=image,
        )
        category_data1 = {"category_name": "얘기해요", "category_url": "talk"}
        category_data2 = {"category_name": "모집해요", "category_url": "join"}
        category_data3 = {"category_name": "공구해요", "category_url": "groupbuy"}
        Category.objects.create(community=community, **category_data1)
        Category.objects.create(community=community, **category_data2)
        Category.objects.create(community=community, **category_data3)
        return community

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.image)

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.bookmarked.filter(id=request.user.id).exists()
        return False


class CommunityListSerializer(serializers.ModelSerializer):
    imageurl = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    feeds = serializers.SerializerMethodField()
    bookmarked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id",
            "title",
            "introduction",
            "communityurl",
            "image",
            "imageurl",
            "is_approval",
            "categories",
            "feeds",
            "bookmarked",
            "is_bookmarked",
        ]

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.image)

    def get_categories(self, obj):
        categories = obj.community_category.all()
        category_name_list = [
            [category.id, category.category_name, category.category_url]
            for category in categories
        ]
        return category_name_list

    def get_feeds(self, obj):
        feeds = Feed.objects.filter(category__community=obj)
        feed = FeedTitleSerializer(feeds, many=True)
        return feed.data

    def get_bookmarked(self, obj):
        return obj.bookmarked.count()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request.user and request.user.is_authenticated:
            return obj.bookmarked.filter(id=request.user.id).exists()
        return False


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
    communityurl = serializers.StringRelatedField(source="community.communityurl")
    introduction = serializers.StringRelatedField(source="community.introduction")
    image = serializers.StringRelatedField(source="community.image")
    imageurl = serializers.SerializerMethodField()

    class Meta:
        model = CommunityAdmin
        fields = [
            "user",
            "title",
            "communityurl",
            "introduction",
            "image",
            "imageurl",
        ]

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.community.image)


class MyCommunityInfoSerializer(serializers.ModelSerializer):
    bookmark_count = serializers.SerializerMethodField()
    feed_count = serializers.SerializerMethodField()
    recent_act = serializers.SerializerMethodField()
    imageurl = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "title",
            "communityurl",
            "introduction",
            "image",
            "imageurl",
            "bookmark_count",
            "feed_count",
            "recent_act",
        ]

    def get_imageurl(self, obj):
        return config("BACKEND_URL") + "/media/" + str(obj.image)

    def get_bookmark_count(self, obj):
        return obj.bookmarked.count()

    def get_feed_count(self, obj):
        category = obj.community_category.all()
        feed = Feed.objects.filter(category_id__in=category)
        grouppurchase = GroupPurchase.objects.filter(category_id__in=category)
        return feed.count() + grouppurchase.count()

    def get_recent_act(self, obj):
        category = obj.community_category.all()
        feed = (
            Feed.objects.filter(category_id__in=category)
            .order_by("created_at")
            .values("created_at")
            .last()
        )
        grouppurchase = (
            GroupPurchase.objects.filter(category_id__in=category)
            .order_by("created_at")
            .values("created_at")
            .last()
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        if not feed and not grouppurchase:
            return "아직 활동이 없습니다"
        if not feed:
            grouppurchase_time = grouppurchase["created_at"].strftime(date_format)
            return grouppurchase
        if not grouppurchase:
            feed_time = feed["created_at"].strftime(date_format)
            return feed_time
        if feed and grouppurchase:
            feed_time = feed["created_at"].strftime(date_format)
            grouppurchase_time = grouppurchase["created_at"].strftime(date_format)
            if feed_time > grouppurchase_time:
                return feed_time
            else:
                return grouppurchase_time


class CommunityAdminSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source="user.email")
    name = serializers.StringRelatedField(source="user.name")
    nickname = serializers.StringRelatedField(source="user.profile.nickname")
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


class CommunityUrlSerializer(serializers.ModelSerializer):
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ["title", "communityurl", "is_bookmarked"]

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request.user and request.user.is_authenticated:
            return obj.bookmarked.filter(id=request.user.id).exists()
        return False


class ForbiddenWordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForbiddenWord
        fields = [
            "word",
        ]


class SearchUserSerializer(serializers.ModelSerializer):
    name = serializers.StringRelatedField(source="user.name")
    nickname = serializers.SerializerMethodField(source="profile.nickname")
    last_login = serializers.StringRelatedField(source="user.last_login")

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "nickname",
            "last_login",
        ]
