from rest_framework import filters, permissions, status
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from community.models import Community, CommunityAdmin, ForbiddenWord
from community.serializers import (
    CommunityUrlSerializer,
    CommunityAdminSerializer,
    CommunityCreateSerializer,
    CommunityCategorySerializer,
)
from django.db.models import Sum
from decouple import config
from collections import OrderedDict
from feed.models import (
    Comment,
    Cocomment,
    GroupPurchaseComment,
    Feed,
    GroupPurchase,
    JoinedUser,
    Category,
    Image,
)
from feed.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CocommentSerializer,
    FeedCreateSerializer,
    FeedDetailSerializer,
    FeedListSerializer,
    FeedCreateSerializer,
    FeedNotificationSerializer,
    GroupPurchaseCreateSerializer,
    GroupPurchaseListSerializer,
    GroupPurchaseDetailSerializer,
    JoinedUserCreateSerializer,
    JoinedUserSerializer,
    GroupPurchaseCommentSerializer,
    GroupPurchaseSelfEndSerializer,
)
import math


class CustomPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["total_pages"] = math.ceil(
            self.page.paginator.count / self.page_size
        )
        response.data["before_page"] = (
            None if self.page.number == 1 else self.page.number - 1
        )
        response.data["re_before_page"] = (
            None if self.page.number < 2 else self.page.number - 2
        )
        response.data["current_page"] = self.page.number
        response.data["after_page"] = (
            None
            if self.page.number >= self.page.paginator.num_pages
            else self.page.number + 1
        )
        response.data["re_after_page"] = (
            None
            if self.page.number >= self.page.paginator.num_pages - 1
            else self.page.number + 2
        )
        url = config("BACKEND_URL")
        response.data["url"] = (
            url
            + "/community"
            + self.request.build_absolute_uri().split("?")[0].split("community")[1]
        )
        return response


class CommentView(APIView):
    """Feed 댓글 CUD view"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, feed_id):
        serializer = CommentCreateSerializer(data=request.data)
        forbidden_word = ForbiddenWord.objects.filter(
            community__community_category__feed_category__id=feed_id
        ).values_list("word", flat=True)
        for word in forbidden_word:
            if word in request.data["text"]:
                return Response(
                    {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if serializer.is_valid():
            serializer.save(user=request.user, feed_id=feed_id)
            feed = get_object_or_404(Feed, id=feed_id)
            comment = feed.comment.all().order_by("-created_at")
            comment_serializer = CommentSerializer(comment, many=True)
            return Response(
                {"message": "댓글을 작성했습니다.", "comment": comment_serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user != request.user:
            return Response(
                {"error": "댓글 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            serializer = CommentCreateSerializer(comment, data=request.data)
            forbidden_word = ForbiddenWord.objects.filter(
                community__community_category__feed_category__comment__id=comment_id
            ).values_list("word", flat=True)
            for word in forbidden_word:
                if word in request.data["text"]:
                    return Response(
                        {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "댓글을 수정했습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user != request.user:
            return Response(
                {"error": "댓글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            comment.delete()
            return Response({"message": "댓글을 삭제했습니다."}, status=status.HTTP_200_OK)


class CocommentView(APIView):
    """Feed 대댓글 CRUD view"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, comment_id):
        cocomment = Cocomment.objects.filter(comment_id=comment_id).order_by(
            "created_at"
        )
        if not cocomment:
            return Response({"message": "대댓글이 없습니다"}, status=status.HTTP_204_NO_CONTENT)
        else:
            serializer = CocommentSerializer(cocomment, many=True)
            return Response(
                {"message": "대댓글을 가져왔습니다", "cocomment": serializer.data},
                status=status.HTTP_200_OK,
            )

    def post(self, request, comment_id):
        serializer = CocommentSerializer(data=request.data)
        forbidden_word = ForbiddenWord.objects.filter(
            community__community_category__feed_category__comment__id=comment_id
        ).values_list("word", flat=True)
        for word in forbidden_word:
            if word in request.data["text"]:
                return Response(
                    {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if serializer.is_valid():
            serializer.save(user=request.user, comment_id=comment_id)
            return Response({"message": "대댓글을 작성했습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, cocomment_id):
        cocomment = get_object_or_404(Cocomment, id=cocomment_id)
        if cocomment.user != request.user:
            return Response(
                {"error": "대댓글 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            forbidden_word = ForbiddenWord.objects.filter(
                community__community_category__feed_category__comment__cocomment__id=cocomment_id
            ).values_list("word", flat=True)
            for word in forbidden_word:
                if word in request.data["text"]:
                    return Response(
                        {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            serializer = CocommentSerializer(cocomment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "대댓글을 수정했습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, cocomment_id):
        cocomment = get_object_or_404(Cocomment, id=cocomment_id)
        if cocomment.user != request.user:
            return Response(
                {"error": "대댓글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            cocomment.delete()
            return Response({"message": "대댓글을 삭제했습니다."}, status=status.HTTP_200_OK)


# class FeedAllView(APIView):
#     """랜덤 커뮤 인기 feed list"""

#     def get(self, request):
#         feeds = Feed.objects.all().order_by("-created_at")[:3]
#         serializer = FeedListSerializer(feeds, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class FeedListView(APIView):
    """feed 전체 리스트 view"""

    pagination_class = CustomPagination()

    def get(self, request, community_url):
        community = Community.objects.get(communityurl=community_url)
        feed_list = Feed.objects.filter(category__community=community).order_by(
            "-created_at"
        )
        if not feed_list:
            return Response(
                {"message": "아직 게시글이 없습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            paginated_feed_list = self.pagination_class.paginate_queryset(
                feed_list, request
            )
            serializer = FeedListSerializer(paginated_feed_list, many=True)
            pagination_serializer = self.pagination_class.get_paginated_response(
                serializer.data
            )
            return Response(pagination_serializer.data, status=status.HTTP_200_OK)


class FeedCategoryListView(APIView):
    """feed 카테고리 리스트 view"""

    pagination_class = CustomPagination()

    def get(self, request, community_url, category_url):
        community_category = get_object_or_404(Community, communityurl=community_url)
        category_serializer = CommunityCategorySerializer(community_category)
        community_title = get_object_or_404(Community, communityurl=community_url)
        community_serializer = CommunityCreateSerializer(
            community_title, context={"request": request}
        )
        category_name = (
            Category.objects.filter(
                community__communityurl=community_url, category_url=category_url
            )
            .first()
            .category_name
        )
        feed_list = Feed.objects.filter(
            category__community__communityurl=community_url,
            category__category_url=category_url,
        ).order_by("-created_at")
        if not feed_list:
            return Response(
                {
                    "community": community_serializer.data,
                    "category_name": category_name,
                    "categories": category_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            paginated_feed_list = self.pagination_class.paginate_queryset(
                feed_list, request
            )
            notification_feed = feed_list.filter(is_notification=True)
            notification_serializer = FeedListSerializer(notification_feed, many=True)
            serializer = FeedListSerializer(paginated_feed_list, many=True)
            pagination_serializer = self.pagination_class.get_paginated_response(
                serializer.data
            )
            return Response(
                {
                    "community": community_serializer.data,
                    "category_name": category_name,
                    "categories": category_serializer.data,
                    "feed": pagination_serializer.data,
                    "notification": notification_serializer.data,
                },
                status=status.HTTP_200_OK,
            )


class FeedDetailView(APIView):
    """feed 상세보기, 수정, 삭제 view"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # 조회수 기능을 위한 모델 세팅
    model = Feed

    # feed 상세 및 comment,cocomment 함께 가져오기
    def get(self, request, community_url, feed_id):
        # community_url이 있어야 prev, next view가 작동합니다!
        feed = get_object_or_404(Feed, id=feed_id)
        community = Category.objects.get(id=feed.category_id).community
        comment = feed.comment.all().order_by("-created_at")
        admin = Category.objects.get(id=feed.category_id).community.comu
        previous = (
            Feed.objects.filter(
                id__lt=feed_id, category__community__communityurl=community_url
            )
            .order_by("-id")
            .first()
        )
        next = (
            Feed.objects.filter(
                id__gt=feed_id, category__community__communityurl=community_url
            )
            .order_by("id")
            .first()
        )

        feed_serializer = FeedDetailSerializer(feed, context={"request": request})
        admin_serializer = CommunityAdminSerializer(admin, many=True)
        commnity_serializer = CommunityUrlSerializer(
            community, context={"request": request}
        )
        comment_serializer = CommentSerializer(comment, many=True)

        feed.click()

        response = {
            "feed": feed_serializer.data,
            "community": commnity_serializer.data,
            "admin": admin_serializer.data,
            "previous": previous.id if previous else None,
            "next": next.id if next else None,
        }
        response["comment"] = comment_serializer.data or "아직 댓글이 없습니다"

        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, community_url, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if feed.user != request.user:
            return Response(
                {"error": "게시글 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            forbidden_word = ForbiddenWord.objects.filter(
                community_id=feed.category.community.id
            ).values_list("word", flat=True)
            if forbidden_word:
                for word in forbidden_word:
                    if word in request.data["content"] or word in request.data["title"]:
                        return Response(
                            {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            serializer = FeedCreateSerializer(feed, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message": "게시글이 수정되었습니다"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, community_url, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        community = Community.objects.get(communityurl=community_url)

        # 유저가 admin인지 확인
        adminuser = CommunityAdmin.objects.filter(
            user=request.user, community=community
        ).last()
        if feed.user != request.user and not adminuser:
            return Response(
                {"message": "게시글 작성자와 관리자만 삭제할 수 있습니다"},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            feed.delete()
            return Response({"message": "게시글을 삭제했습니다"}, status=status.HTTP_200_OK)


class FeedCreateView(APIView):
    """feed 생성 view"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_url):
        serializer = FeedCreateSerializer(data=request.data)
        category = get_object_or_404(Category, id=request.data["category_id"])
        forbidden_word = ForbiddenWord.objects.filter(
            community_id=category.community.id
        ).values_list("word", flat=True)
        if forbidden_word:
            for word in forbidden_word:
                if word in request.data["content"] or word in request.data["title"]:
                    return Response(
                        {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        if serializer.is_valid():
            serializer.save(user=request.user, category_id=request.data["category_id"])
            return Response({"message": "게시글이 작성되었습니다"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeView(APIView):
    """좋아요 기능"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if request.user in feed.likes.all():
            feed.likes.remove(request.user)
            return Response("좋아요를 취소했습니다.", status=status.HTTP_200_OK)
        else:
            feed.likes.add(request.user)
            return Response("좋아요👍를 눌렀습니다.", status=status.HTTP_200_OK)


class FeedNotificationView(APIView):
    """권한에 따라 Feed 공지글 설정/취소"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        community = Category.objects.get(id=feed.category_id).community

        # 유저가 admin인지 확인
        user = CommunityAdmin.objects.filter(
            user=request.user, community=community
        ).last()
        if not user:
            return Response(
                {"message": "커뮤니티 관리자 권한이 없습니다"}, status=status.HTTP_403_FORBIDDEN
            )

        notification_count = Feed.objects.filter(
            is_notification=True, category_id=feed.category_id
        ).count()
        if notification_count > 4:
            return Response(
                {"message": "카테고리당 공지는 5개까지 가능합니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializer = FeedNotificationSerializer(feed, data=request.data)
            is_notificated = serializer.post_is_notification(feed, community, request)
            serializer.is_valid(raise_exception=True)
            if is_notificated:
                serializer.save(is_notification=False)
                return Response(
                    {"data": serializer.data, "message": "공지가 취소되었습니다"},
                    status=status.HTTP_200_OK,
                )
            else:  # False일 경우
                serializer.save(is_notification=True)
                return Response(
                    {"data": serializer.data, "message": "공지가 등록되었습니다"},
                    status=status.HTTP_200_OK,
                )


class FeedSearchView(ListAPIView):
    """Feed 검색"""

    search_fields = (
        "title",
        "content",
    )
    filter_backends = [filters.SearchFilter]
    queryset = Feed.objects.all()
    serializer_class = FeedListSerializer


class GroupPurchaseCreateView(APIView):
    """공구 게시글 get, 생성 view"""

    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request, community_url):
        community = get_object_or_404(Community, communityurl=community_url)
        category = get_object_or_404(
            Category, community=community, category_url="groupbuy"
        )
        grouppruchase = GroupPurchase.objects.filter(
            community_id=community.id, category_id=category.id
        )
        serializer = GroupPurchaseCreateSerializer(grouppruchase, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, community_url):
        serializer = GroupPurchaseCreateSerializer(data=request.data)
        community = get_object_or_404(Community, communityurl=community_url)
        category = get_object_or_404(
            Category, community=community, category_url="groupbuy"
        )
        forbidden_word = ForbiddenWord.objects.filter(
            community_id=category.community.id
        ).values_list("word", flat=True)
        if forbidden_word:
            for word in forbidden_word:
                if word in request.data["content"] or word in request.data["title"]:
                    return Response(
                        {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        if serializer.is_valid():
            serializer.validate_datetime(request.data)
            serializer.save(community=community, category=category, user=request.user)
            return Response(
                {"message": "공동구매 게시글이 작성되었습니다"}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupPurchaseDetailView(APIView):
    """공구 상세 get, update, delete view"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 조회수 기능을 위한 모델 세팅
    model = GroupPurchase

    # 공구 상세 및 comment,cocomment 함께 가져오기
    def get(self, request, community_url, grouppurchase_id):
        purchasefeed = get_object_or_404(GroupPurchase, id=grouppurchase_id)
        purchase_serializer = GroupPurchaseDetailSerializer(purchasefeed)
        community = Community.objects.get(communityurl=community_url)
        commnity_serializer = CommunityUrlSerializer(
            community, context={"request": request}
        )
        purchase_comment = purchasefeed.p_comment.all().order_by("created_at")
        comment_serializer = CommentSerializer(purchase_comment, many=True)

        purchasefeed.click()

        response = {
            "grouppurchase": purchase_serializer.data,
            "community": commnity_serializer.data,
        }
        # 댓글 유무 여부 확인
        response["comment"] = comment_serializer.data or "아직 댓글이 없습니다"
        return Response(response, status=status.HTTP_200_OK)

    def put(self, request, community_url, grouppurchase_id):
        purchasefeed = get_object_or_404(GroupPurchase, id=grouppurchase_id)
        community = get_object_or_404(Community, communityurl=community_url)
        category = get_object_or_404(
            Category, community=community, category_url="groupbuy"
        )
        forbidden_word = ForbiddenWord.objects.filter(
            community_id=category.community.id
        ).values_list("word", flat=True)
        if forbidden_word:
            for word in forbidden_word:
                if word in request.data["content"] or word in request.data["title"]:
                    return Response(
                        {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        if purchasefeed.user != request.user:
            return Response(
                {"error": "공구 게시글 작성자만 수정할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializer = GroupPurchaseCreateSerializer(purchasefeed, data=request.data)
            if serializer.is_valid():
                serializer.validate_datetime_update(request.data)
                serializer.save(
                    community=community, category=category, user=request.user
                )
                return Response(
                    {"message": "공구 게시글이 수정되었습니다"}, status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, community_url, grouppurchase_id):
        purchasefeed = get_object_or_404(GroupPurchase, id=grouppurchase_id)
        if purchasefeed.user != request.user:
            return Response(
                {"error": "공구 게시글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            if not purchasefeed.is_ended:
                purchasefeed.delete()
                return Response(
                    {"message": "공동구매 게시글을 삭제했습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "이미 종료된 공구 게시글은 삭제할 수 없습니다"},
                    status=status.HTTP_405_METHOD_NOT_ALLOWED,
                )


class GroupPurchaseListView(APIView):
    """공구 list view"""

    def get(self, request, community_url):
        community = get_object_or_404(Community, communityurl=community_url)
        feed_list = (
            GroupPurchase.objects.filter(community_id=community.id)
            .order_by("-created_at")
            .order_by("-is_ended")
        )
        if not feed_list:
            return Response(
                {"message": "아직 게시글이 없습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            serializer = GroupPurchaseListSerializer(feed_list, many=True)
            return Response(
                {"message": "공동구매 게시글 목록을 가져왔습니다", "data": serializer.data},
                status=status.HTTP_200_OK,
            )


class GroupPurchaseJoinedUserView(APIView):
    """공구 참여 유저 CUD view"""

    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, community_url, grouppurchase_id):
        purchasefeed = get_object_or_404(GroupPurchase, id=grouppurchase_id)
        purchase_quantity = (
            JoinedUser.objects.exclude(user=request.user)
            .filter(grouppurchase_id=grouppurchase_id)
            .aggregate(Sum("product_quantity"))
            .get("product_quantity__sum")
            or 0
        )
        remain_quantity = purchasefeed.product_number - purchase_quantity
        join_purchase = JoinedUser.objects.filter(
            user_id=request.user.id, grouppurchase_id=grouppurchase_id
        ).last()
        quantity = int(request.data.__getitem__("product_quantity"))
        if not request.user.profile.region:
            return Response(
                {"message": "유저 프로필을 업데이트 해주세요! 상세 정보가 없으면 공구를 진행할 수 없습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if purchasefeed.check_end_person_limit_point(grouppurchase_id):
            return Response(
                {"message": "공구 인원이 모두 찼습니다!"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        if purchasefeed.is_ended:
            return Response(
                {"message": "이미 종료된 공구입니다!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not join_purchase:
            if quantity < 1:
                return Response(
                    {"message": "수량을 다시 확인해주세요."}, status=status.HTTP_400_BAD_REQUEST
                )
            serializer = JoinedUserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, grouppurchase_id=grouppurchase_id)
            # save한 후 join인원 체크 및 마감여부 확인
            if purchasefeed.check_end_person_limit_point(grouppurchase_id):
                pass
            return Response(
                {
                    "message": "공구를 신청했습니다.",
                },
                status=status.HTTP_201_CREATED,
            )
        # True
        joined_user = JoinedUser.objects.get(
            user_id=request.user.id, grouppurchase_id=grouppurchase_id
        )
        serializer = JoinedUserSerializer(joined_user, data=request.data)
        if quantity < 0 or quantity == joined_user.product_quantity:
            return Response(
                {"message": "수량을 다시 확인해주세요"}, status=status.HTTP_400_BAD_REQUEST
            )
        if quantity > remain_quantity:
            return Response(
                {"message": "신청 수량이 남은 수량보다 많습니다."},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        serializer.is_valid(raise_exception=True)
        if joined_user.is_deleted is True:
            serializer.save(is_deleted=False)
            return Response(
                {"message": "공구를 재 신청했습니다.", "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        if quantity <= 0:
            serializer.save(is_deleted=True)
            return Response(
                {"message": "공구 신청을 취소했습니다.", "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        if quantity != joined_user.product_quantity:
            serializer.save()
            return Response(
                {"message": "공구 수량을 수정했습니다.", "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(
                {"message": "알 수 없는 오류!", "data": serializer.data},
                status=status.HTTP_408_REQUEST_TIMEOUT,
            )


class GroupPurchaseSelfEndView(APIView):
    """작성유저 공구 종료 view"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_url, grouppurchase_id):
        purchase = get_object_or_404(GroupPurchase, id=grouppurchase_id)
        if purchase.is_ended:
            return Response(
                {"message": "이미 종료된 공구 게시글입니다"},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        serializer = GroupPurchaseSelfEndSerializer(purchase, data=request.data)
        if serializer.is_valid():
            serializer.save(is_ended=True)
            return Response(
                {"message": "공동구매 모집을 종료했습니다", "data": serializer.data},
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupPurchaseCommentView(APIView):
    """공구게시글 댓글 CUD view"""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, community_url, grouppurchase_id):
        serializer = GroupPurchaseCommentSerializer(data=request.data)
        forbidden_word = ForbiddenWord.objects.filter(
            community__community__id=grouppurchase_id
        ).values_list("word", flat=True)
        for word in forbidden_word:
            if word in request.data["text"]:
                return Response(
                    {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if serializer.is_valid():
            serializer.save(user=request.user, grouppurchase_id=grouppurchase_id)
            return Response(
                {"message": "공구 댓글을 작성했습니다."}, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, purchase_comment_id):
        purchase_comment = get_object_or_404(
            GroupPurchaseComment, id=purchase_comment_id
        )
        forbidden_word = ForbiddenWord.objects.filter(
            community__community__p_comment__id=purchase_comment_id
        ).values_list("word", flat=True)
        for word in forbidden_word:
            if word in request.data["text"]:
                return Response(
                    {"message": f"금지어 '{word}' 이/가 포함되어 있습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if purchase_comment.user != request.user:
            return Response(
                {"error": "댓글 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            serializer = GroupPurchaseCommentSerializer(
                purchase_comment, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "공구 댓글을 수정했습니다."}, status=status.HTTP_200_OK
                )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, purchase_comment_id):
        purchase_comment = get_object_or_404(
            GroupPurchaseComment, id=purchase_comment_id
        )
        if purchase_comment.user != request.user:
            return Response(
                {"error": "댓글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            purchase_comment.delete()
            return Response({"message": "공구 댓글을 삭제했습니다."}, status=status.HTTP_200_OK)


class ImageUploadAndDeleteView(APIView):
    def post(self, request):
        image = request.FILES.get("image")
        if image:
            image = Image.objects.create(image=image)
            imageurl = config("BACKEND_URL") + image.image.url
            image.delete()
            return Response(
                {"message": "이미지 업로드 성공", "image_url": imageurl},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "이미지 업로드 실패"}, status=status.HTTP_400_BAD_REQUEST
            )
