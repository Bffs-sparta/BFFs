from rest_framework import serializers
from feed.models import Feed, Comment, Cocomment, Category, GroupPurchase, JoinedUser
from community.models import CommunityAdmin
from community.serializers import CommunityAdminSerializer
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404


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
            "text",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class CommentSerializer(serializers.ModelSerializer):
    """댓글 serializer"""

    class Meta:
        model = Comment
        fields = [
            "text",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
        }


class FeedListSerializer(serializers.ModelSerializer):
    """feed list serializer"""

    # user = serializers.SerializerMethodField('get_user_prefetch_related')
    class Meta:
        model = Feed
        fields = [
            "user",
            # "nickname",
            "title",
            "image",
            "view_count",
            "created_at",
            "category",
        ]

    # def get_user_prefetch_related(self, obj):
    #     user_data = obj.user
    #     datas = []
    #     for data in user_data:
    #         data = {'id': user.id, 'nickname':user.nickname}
    #         datas.append(data)
    #     return datas


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
            "community": {"read_only": True},
        }


class FeedDetailSerializer(serializers.ModelSerializer):
    """feed 상세 serializer"""

    likes_count = serializers.SerializerMethodField()
    likes = serializers.StringRelatedField(many=True)

    class Meta:
        model = Feed
        fields = "__all__"
        extra_kwargs = {
            "id": {"read_only": True},
            "user": {"read_only": True},
            "created_at": {"read_only": True},
            "updated_at": {"read_only": True},
            "likes": {"read_only": True},
        }

    def get_likes_count(self, obj):
        return obj.likes.count()


class FeedNotificationSerializer(serializers.ModelSerializer):
    """feed 공지 serializer"""

    class Meta:
        model = Feed
        fields = [
            "is_notification",
        ]

    # is_admin여부를 확인해 공지글로 바꾸어줄 수 있도록 구현
    def post_is_notification(self, obj, request):
        user = get_object_or_404(CommunityAdmin, user=request.user)
        if user.is_subadmin != True and user.is_comuadmin != True:
            return Response({"message": "커뮤니티 관리자 권한이 없습니다"})
        else:
            if (user.is_subadmin or user.is_comuadmin) and obj.is_notification == False:
                return False
            elif (
                user.is_subadmin or user.is_comuadmin
            ) and obj.is_notification == True:
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
