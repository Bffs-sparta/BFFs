from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from feed.models import Feed, Comment, Cocomment
from community.models import Community
from rest_framework import generics
from rest_framework import filters


from feed.serializers import (
    FeedListSerializer,
    FeedDetailSerializer,
    FeedCreateSerializer,
    CommentSerializer,
    GroupPurchaseSerializer,
    CocommentSerializer,
)


class CommentView(APIView):
    # comment CUD view
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, feed_id):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, feed_id=feed_id)
            return Response({"message": "댓글을 작성했습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if comment.user != request.user:
            return Response(
                {"error": "댓글 작성자만 수정할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            serializer = CommentSerializer(comment, data=request.data)
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
    # 대댓글 cocomment CRUD view
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

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        serializer = CocommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, comment_id=comment_id)
            return Response({"message": "대댓글을 작성했습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, cocomment_id):
        cocomment = get_object_or_404(Cocomment, id=cocomment_id)
        if cocomment.user != request.user:
            return Response(
                {"error": "대댓글 작성자만 수정할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
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


class FeedListView(APIView):
    # feed 전체 리스트 view
    def get(self, request, community_name):
        community = Community.objects.get(title=community_name)
        feed_list = Feed.objects.filter(community_id=community.id).order_by(
            "-created_at"
        )
        if not feed_list:
            return Response(
                {"message": "아직 게시글이 없습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            serializer = FeedListSerializer(feed_list)
            return Response(serializer.data, status=status.HTTP_200_OK)


class FeedCategoryListView(APIView):
    # feed 카테고리 리스트 view
    def get(self, request, community_name, category_name):
        print("⭐️")
        community = Community.objects.get(title=community_name)
        feed_list = Feed.objects.filter(category=category_name).order_by("-created_at")
        print("⭐️⭐️")

        if not feed_list:
            return Response(
                {"message": "아직 카테고리 게시글이 없습니다."}, status=status.HTTP_204_NO_CONTENT
            )
        else:
            serializer = FeedListSerializer(feed_list)
            return Response(serializer.data, status=status.HTTP_200_OK)


class FeedDetailView(APIView):
    # feed 상세보기, 수정, 삭제 view
    # 조회수 기능을 위한 모델 세팅
    model = Feed

    # feed 상세 및 comment,cocomment 함께 가져오기
    def get(self, request, community_name, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        community = Community.objects.get(title=community_name)
        serializer = FeedDetailSerializer(feed)
        comment = feed.comment.all().order_by("created_at")
        # 댓글 유무 여부 확인
        if not comment:
            return Response(
                {
                    "message": "조회수 +1",
                    "feed": serializer.data,
                    "comment": "아직 댓글이 없습니다",
                },
                status=status.HTTP_200_OK,
            )
        else:
            comment_serializer = CommentSerializer(comment, many=True)
            # feed를 get할 때 조회수 올리기
            feed.click
            return Response(
                {
                    "message": "조회수 +1",
                    "feed": serializer.data,
                    "comment": comment_serializer.data,
                },
                status=status.HTTP_200_OK,
            )

    # feed 조회수 기능 => get할때 조회수가 올라가도록 바꾸기! 작동 확인 후 주석 및 코드 삭제하도록 하겠음
    # def post(self, request, feed_id):
    #     feed = get_object_or_404(Feed, id=feed_id)
    #     feed.click
    #     return Response("조회수 +1", status=status.HTTP_200_OK)

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if feed.user != request.user:
            return Response(
                {"error": "게시글 작성자만 수정할 수 있습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        else:
            serializer = FeedCreateSerializer(feed, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response({"message": "게시글이 수정되었습니다"}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if feed.user != request.user:
            return Response(
                {"error": "게시글 작성자만 삭제할 수 있습니다."}, status=status.HTTP_403_FORBIDDEN
            )
        else:
            feed.delete()
            return Response({"message": "게시글을 삭제했습니다."}, status=status.HTTP_200_OK)


class FeedCreateView(APIView):
    # feed 생성 view
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, community_name):  # testcomu
        serializer = FeedCreateSerializer(data=request.data)
        community = Community.objects.get(title=community_name)
        if serializer.is_valid():
            serializer.save(community=community, user=request.user)
            return Response({"message": "게시글이 작성되었습니다"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeView(APIView):
    # 좋아요 기능
    def post(self, request, feed_id):
        feed = get_object_or_404(Feed, id=feed_id)
        if request.user in feed.likes.all():
            feed.likes.remove(request.user)
            return Response("좋아요를 취소했습니다.", status=status.HTTP_200_OK)
        else:
            feed.likes.add(request.user)
            return Response("좋아요👍를 눌렀습니다.", status=status.HTTP_200_OK)


class FeedNotificationView(APIView):
    def post(self, request, feed_id):
        feed = Feed.objects.get(id=feed_id)
        if feed:
            serializer = FeedDetailSerializer(feed, data=request.data)
            is_notificated = serializer.post_is_notification(feed, request)
            serializer.is_notification = is_notificated
            serializer.save()
            return Response({"message": "게시글 상태가 변경되었습니다"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "유효하지 않은 요청입니다"}, status=status.HTTP_400_BAD_REQUEST
            )


class FeedSearchView(ListAPIView):
    search_fields = (
        "user",
        "title",
        "content",
        "created_at",
        "text",
    )
    filter_backends = filters.SearchFilter
    queryset = Feed.objects.all()
    serializer_class = FeedListSerializer, CommentSerializer
