from django.urls import path
from .views import (
    FeedAllView,
    FeedDetailView,
    FeedCreateView,
    CommentView,
    CommentView,
    CocommentView,
    CocommentView,
    GroupPurchaseCreateView,
    GroupPurchaseDetailView,
    ImageUploadAndDeleteView,
)

urlpatterns = [
    # 전체 feed 조회
    path("", FeedAllView.as_view(), name="feed_view"),
    # 개별 feed 수정 삭제
    path("<int:feed_id>/", FeedDetailView.as_view(), name="feed_detail_view"),
    # feed 생성
    path(
        "<int:category_id>/feed/",
        FeedCreateView.as_view(),
        name="feed_create_view",
    ),
    # comment 생성
    path(
        "<int:feed_id>/comment/",
        CommentView.as_view(),
        name="comment_create_view",
    ),
    # comment 수정 삭제
    path(
        "comment/<int:comment_id>/",
        CommentView.as_view(),
        name="comment_put_delete_view",
    ),
    # 대댓글, cocomment get 생성
    path(
        "<int:comment_id>/cocomment/",
        CocommentView.as_view(),
        name="cocomment_create_view",
    ),
    # cocomment 수정 삭제
    path(
        "cocomment/<int:cocomment_id>/",
        CocommentView.as_view(),
        name="cocomment_put_delete_view",
    ),
    # grouppurchase 게시글 생성
    path(
        "<str:community_name>/grouppurchase/",
        GroupPurchaseCreateView.as_view(),
        name="grouppurchase_create_view",
    ),
    # grouppurchase 게시글 수정 삭제
    path(
        "grouppurchase/<int:grouppurchase_id>/",
        GroupPurchaseDetailView.as_view(),
        name="grouppurchase_put_delete_view",
    ),
    path("image/upload/", ImageUploadAndDeleteView.as_view(), name="image_upload_view"),
    # grouppurchase 참여 / 취소
    path(
        "<int:grouppurchase_id>/join/",
        GroupPurchaseJoinedUserView.as_view(),
        name="grouppurchase_join_view",
    ),
]
