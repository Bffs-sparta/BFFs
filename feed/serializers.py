from datetime import datetime
from rest_framework import serializers
from rest_framework.response import Response

from feed.models import (
    Category,
    Comment,
    Cocomment,
    Feed,
    GroupPurchase,
    JoinedUser,
    GroupPurchaseComment,
)
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

    user_id = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Cocomment
        fields = [
            "id",
            "user",
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

    def get_nickname(self, obj):
        return Profile.objects.get(id=obj.user_id).nickname
    def get_user_id(self, obj):
        return Profile.objects.get(user=obj.user).id


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "text",
        ]

    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        return comment


class CommentSerializer(serializers.ModelSerializer):
    """댓글 serializer"""

    user_id = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()
    cocomment = CocommentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user_id",
            "nickname",
            "text",
            "created_at",
            "updated_at",
            "cocomment",
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
        return Profile.objects.get(user=obj.user).nickname

    def get_cocomment(self, obj):
        return obj.cocomment.all()


class FeedTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = [
            "id",
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
            "content",
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
    like_bool = serializers.SerializerMethodField()

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
            "like_bool": {"read_only": True},
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_nickname(self, obj):
        return Profile.objects.get(user=obj.user).nickname

    def get_category(self, obj):
        return Category.objects.get(id=obj.category_id).category_name

    def get_like_bool(self, obj):
        request = self.context.get("request")
        if request.user in obj.likes.all():
            return True
        else:
            return False


class ProfileFeedSerializer(serializers.ModelSerializer):
    """feed 상세 serializer"""

    nickname = serializers.SerializerMethodField()

    class Meta:
        model = Feed
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "nickname": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_nickname(self, obj):
        return Profile.objects.get(user=obj.user).nickname


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

    grouppurchase_status = serializers.SerializerMethodField()

    class Meta:
        model = GroupPurchase
        fields = [
            "title",
            "product_name",
            "person_limit",
            "location",
            "user",
            "open_at",
            "close_at",
            "is_ended",
            "created_at",
            "grouppurchase_status",
        ]

    def get_grouppurchase_status(self, obj):
        now = datetime.now()
        is_ended = obj.is_ended
        open_at = datetime.strptime(str(obj.open_at), "%Y-%m-%d %H:%M:%S")
        if not obj.close_at:
            if is_ended == True:
                return "종료"
            elif is_ended == False and open_at > now:
                return "시작 전"
            elif is_ended == False and open_at < now:
                return "진행 중"

        else:
            close_at = datetime.strptime(str(obj.close_at), "%Y-%m-%d %H:%M:%S")
            if is_ended == True:
                return "종료"
            elif close_at < now:
                # cron 작동 안했을 경우에도 종료 시간에따라 종료를 띄워주기
                return "종료"
            elif is_ended == False and open_at > now:
                return "시작 전"
            elif close_at and is_ended == False and close_at > now and open_at < now:
                return "진행 중"


class GroupPurchaseDetailSerializer(serializers.ModelSerializer):
    """공구 게시글 상세 serializer"""

    grouppurchase_status = serializers.SerializerMethodField()

    class Meta:
        model = GroupPurchase
        fields = "__all__"

    def get_grouppurchase_status(self, obj):
        now = datetime.now()
        is_ended = obj.is_ended
        open_at = datetime.strptime(str(obj.open_at), "%Y-%m-%d %H:%M:%S")
        if not obj.close_at:
            if is_ended == True:
                return "종료"
            elif is_ended == False and open_at > now:
                return "시작 전"
            elif is_ended == False and open_at < now:
                return "진행 중"

        else:
            close_at = datetime.strptime(str(obj.close_at), "%Y-%m-%d %H:%M:%S")
            if is_ended == True:
                return "종료"
            elif close_at < now:
                # cron 작동 안했을 경우에도 종료 시간에따라 종료를 띄워주기
                return "종료"
            elif is_ended == False and open_at > now:
                return "시작 전"
            elif close_at and is_ended == False and close_at > now and open_at < now:
                return "진행 중"


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
            "user": {"read_only": True},
            "community": {"read_only": True},
            "category": {"read_only": True},
        }

    def validate_datetime(self, data):
        now = datetime.now()
        open_at = datetime.strptime(data.get("open_at"), "%Y-%m-%dT%H:%M:%S")
        close_at = datetime.strptime(data.get("close_at"), "%Y-%m-%dT%H:%M:%S")
        meeting_at = datetime.strptime(data.get("meeting_at"), "%Y-%m-%dT%H:%M:%S")
        if now >= open_at and meeting_at < open_at:
            raise serializers.ValidationError({"error": "현재 이후의 시점을 선택해주세요."})
        if close_at and open_at > close_at:
            raise serializers.ValidationError({"error": "공구 시작 시간보다 이후의 시점을 선택해주세요."})
        if close_at and meeting_at < close_at:
            raise serializers.ValidationError({"error": "공구가 끝나는 시간보다 이후의 시점을 선택해주세요."})
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


class GroupPurchaseCommentSerializer(serializers.ModelSerializer):
    """공구 댓글 serializer"""

    user_id = serializers.SerializerMethodField()
    nickname = serializers.SerializerMethodField()

    class Meta:
        model = GroupPurchaseComment
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
        return Profile.objects.get(user=obj.user).nickname
