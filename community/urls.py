from django.urls import path
from .views import (
    CommunityView,
    CommunitySubAdminView,
    CommunityForbiddenView,
    CommunityBookmarkView,
    SearchCommunityView,
    SearchUserView,
)
from feed.views import (
    FeedListView,
    FeedCategoryListView,
    FeedDetailView,
    LikeView,
    FeedNotificationView,
    GroupPurchaseListView,
    GroupPurchaseDetailView,
    GroupPurchaseJoinedUserView,
)

urlpatterns = [
    path("", CommunityView.as_view(), name="community_view"),
    path(
        "<str:community_name>/",
        CommunityView.as_view(),
        name="community_detail_view",
    ),
    path(
        "<str:community_name>/subadmin/",
        CommunitySubAdminView.as_view(),
        name="community_subadmin_view",
    ),
    path(
        "<str:community_name>/forbidden/",
        CommunityForbiddenView.as_view(),
        name="community_forbidden_view",
    ),
    path(
        "<str:community_name>/bookmark/",
        CommunityBookmarkView.as_view(),
        name="community_bookmark_view",
    ),
    path("search/", SearchCommunityView.as_view(), name="search_community_view"),
    path("searchuser/", SearchUserView.as_view(), name="search_user_view"),
    # feed 전체 list get
    path(
        "<str:community_name>/list/",
        FeedListView.as_view(),
        name="feed_list_view",
    ),
    # feed 카테고리 list get
    path(
        "<str:community_name>/category/<str:category_name>/",
        FeedCategoryListView.as_view(),
        name="feed_category_list_view",
    ),
    # feed 상세, comment get
    path(
        "<str:community_name>/<int:feed_id>/",
        FeedDetailView.as_view(),
        name="feed_detail_view",
    ),
    # like 설정/취소
    path("<int:feed_id>/likes/", LikeView.as_view(), name="like_view"),
    # feed 게시글 공지 설정/취소
    path(
        "<int:feed_id>/notification/",
        FeedNotificationView.as_view(),
        name="feed_notification_view",
    ),
    # grouppurchase 전체 list
    path(
        "<str:community_name>/grouppurchase/",
        GroupPurchaseListView.as_view(),
        name="grouppurchase_list_view",
    ),
    # grouppurchase 상세 페이지
    path(
        "<str:community_name>/grouppurchase/<int:grouppurchase_id>/",
        GroupPurchaseDetailView.as_view(),
        name="grouppurchase_detail_view",
    ),
    # grouppurchase 참여 / 취소
    path(
        "<int:grouppurchase_id>/join/",
        GroupPurchaseJoinedUserView.as_view(),
        name="grouppurchase_join_view",
    ),
]
