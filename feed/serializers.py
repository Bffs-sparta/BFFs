from rest_framework import serializers
from feed.models import Feed, Comment, Cocomment, Category, GroupPurchase
from community.models import CommunityAdmin
from user.serializers import UserCreateSerializer
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "category_name",
        ]


class CocommentSerializer(serializers.ModelSerializer):
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


class FeedCreateSerializer(serializers.ModelSerializer):
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

    # is_admin여부를 확인해 공지글로 바꾸어줄 수 있도록 구현
    def post_is_notification(self, obj, request):
        user = CommunityAdmin.objects.filter(user=request.user)
        print("🐛", user)
        if user.is_subadmin != True or user.is_comuadmin != True:
            return Response({"message": "커뮤니티 관리자 권한이 없습니다"})
        else:
            if (user.is_subadmin or user.is_comuadmin) and obj.is_notification == False:
                return True
            elif (
                user.is_subadmin or user.is_comuadmin
            ) and obj.is_notification == True:
                return False


class GroupPurchaseSerializer(serializers.ModelSerializer):
    # 공구 게시글 내용
    class Meta:
        model = GroupPurchase
        fields = "__all__"

    def validate_datetime(self, data):
        now = timezone.now
        started_at = data.get("started_at")
        ended_at = data.get("ended_at")
        if now > started_at:
            raise serializers.ValidationError({"error": "현재 이후의 시점을 선택해주세요."})
        if ended_at and started_at > ended_at:
            raise serializers.ValidationError({"error": "시작 시간보다 이후의 시점을 선택해주세요."})
        return data


class FeedSearchSerializer(serializers.ModelSerializer):
    # 피드 검색 serializer
    class Meta:
        model = Feed
        fields = "__all__"
        exclude = [
            "image",
            "video",
        ]
