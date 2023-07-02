from django.urls import path
from .views import (
    FeedSearchView,
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
    GroupPurchaseCommentView,
    GroupPurchaseSelfEndView,
)

urlpatterns = [
    path("search", FeedSearchView.as_view(), name="search_community_view"),
    # 전체 feed 조회
    path("", FeedAllView.as_view(), name="feed_view"),
    # 개별 feed 수정
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
        "<str:community_url>/grouppurchase/",
        GroupPurchaseCreateView.as_view(),
        name="grouppurchase_create_view",
    ),
    # grouppurchase 게시글 수정 삭제
    path(
        "<str:community_url>/grouppurchase/<int:grouppurchase_id>/",
        GroupPurchaseDetailView.as_view(),
        name="grouppurchase_put_delete_view",
    ),
    path("image/upload/", ImageUploadAndDeleteView.as_view(), name="image_upload_view"),
    # grouppurchase 작성자 모집 끝 옵션
    path(
        "<int:grouppurchase_id>/self_end/",
        GroupPurchaseSelfEndView.as_view(),
        name="purchase_self_end_view",
    ),
    # grouppurchase comment 생성
    path(
        "<int:grouppurchase_id>/purchasecomment/",
        GroupPurchaseCommentView.as_view(),
        name="purchase_comment_create_view",
    ),
    # grouppurchase comment 수정 삭제
    path(
        "purchasecomment/<int:purchase_comment_id>/",
        GroupPurchaseCommentView.as_view(),
        name="purchase_comment_put_delete_view",
    ),
]
