from django.utils import timezone
from rest_framework import serializers
from rest_framework.response import Response

from community.models import CommunityAdmin
from feed.models import Category, Comment, Cocomment, Feed, GroupPurchase, JoinedUser
from user.models import Profile


class CategorySerializer(serializers.ModelSerializer):
    """카테고리 serializer"""

    class Meta:
        model = Category
        fields = [
            "category_name",
        ]


class CocommentSerializer(serializers.ModelSerializer):
    """대댓글 serializer"""

    class Meta:
        model = Cocomment
        fields = [
            "id" "user",
            "text",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "text",
        ]


class CommentSerializer(serializers.ModelSerializer):
    """댓글 serializer"""

    user_id = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user_id",
            "nickname",
            "text",
            "created_at",
            "updated_at",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_user_id(self, obj):
        return Profile.objects.get(user=obj.user).id

    def get_nickname(self, obj):
        print(Profile.objects.get(user=obj.user).nickname)
        print(obj.user)
        return Profile.objects.get(user=obj.user).nickname


class FeedTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = [
            "category",
            "title",
            "view_count",
        ]


class FeedListSerializer(serializers.ModelSerializer):
    nickname = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = [
            "id",
            "user",
            "nickname",
            "title",
            "image",
            "view_count",
            "created_at",
            "category",
            "comments_count",
            "likes_count",
        ]

    def get_nickname(self, obj):
        return Profile.objects.get(user=obj.user).nickname

    def get_category(self, obj):
        return Category.objects.get(id=obj.category_id).category_name

    def get_comments_count(self, obj):
        comment = obj.comment.count()
        cocomment = obj.comment.prefetch_related("cocomment").count()
        return comment + cocomment

    def get_likes_count(self, obj):
        return obj.likes.count()


class FeedCreateSerializer(serializers.ModelSerializer):
    """feed 생성 serializer"""

    class Meta:
        model = Feed
        fields = [
            "title",
            "content",
            "image",
            "video",
            "category",
        ]
        extra_kwargs = {
            "category": {"read_only": True},
        }


class FeedDetailSerializer(serializers.ModelSerializer):
    """feed 상세 serializer"""

    likes_count = serializers.SerializerMethodField()
    likes = serializers.StringRelatedField(many=True)
    nickname = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "nickname": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "likes": {"read_only": True},
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_nickname(self, obj):
        return Profile.objects.get(user=obj.user).nickname

    def get_category(self, obj):
        return Category.objects.get(id=obj.category_id).category_name


class FeedNotificationSerializer(serializers.ModelSerializer):
    """feed 공지 serializer"""

    class Meta:
        model = Feed
        fields = [
            "is_notification",
        ]

    # is_admin여부를 확인해 공지글로 바꾸어줄 수 있도록 구현
    def post_is_notification(self, obj, community, request):
        if obj.is_notification == False:
            return False
        elif obj.is_notification == True:
            return True


class GroupPurchaseListSerializer(serializers.ModelSerializer):
    """공구 게시글 list serializer"""

    class Meta:
        model = GroupPurchase
        fields = [
            "title",
            "product_name",
            "person_limit",
            "is_joined",
            "location",
            "user",
            "open_at",
            "close_at",
            "is_ended",
            "created_at",
        ]


class GroupPurchaseDetailSerializer(serializers.ModelSerializer):
    """공구 게시글 상세 serializer"""

    class Meta:
        model = GroupPurchase
        fields = "__all__"


class GroupPurchaseCreateSerializer(serializers.ModelSerializer):
    """공구 게시글 생성 serializer"""

    class Meta:
        model = GroupPurchase
        fields = [
            "title",
            "content",
            "product_name",
            "product_number",
            "product_price",
            "link",
            "person_limit",
            "location",
            "meeting_at",
            "open_at",
            "close_at",
            "end_option",
        ]
        extra_kwargs = {
            "community": {"read_only": True},
            "category": {"read_only": True},
        }

    def validate_datetime(self, data):
        now = timezone.now
        started_at = data.get("started_at")
        ended_at = data.get("ended_at")
        if now > started_at:
            raise serializers.ValidationError({"error": "현재 이후의 시점을 선택해주세요."})
        if ended_at and started_at > ended_at:
            raise serializers.ValidationError({"error": "시작 시간보다 이후의 시점을 선택해주세요."})
        return data


class JoinedUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedUser
        fields = [
            "product_quantity",
        ]
        extra_kwargs = {
            "user": {"read_only": True},
            "grouppurchase": {"read_only": True},
            "created_at": {"read_only": True},
            "is_deleted": {"read_only": True},
        }


class JoinedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = JoinedUser
        fields = "__all__"
        extra_kwargs = {
            "user": {"read_only": True},
            "grouppurchase": {"read_only": True},
        }


class FeedSearchSerializer(serializers.ModelSerializer):
    """피드 검색 serializer"""

    class Meta:
        model = Feed
        fields = "__all__"
        exclude = [
            "image",
            "video",
        ]
