from django.urls import path, include
from .views import (
    CommunityView,
    CommunityDetailView,
    CommunitySubAdminView,
    CommunityForbiddenView,
    CommunityBookmarkView,
    SearchCommunityView,
    CommunityCategoryView,
    FeedNextView,
    FeedPrevView,
)
from feed.views import (
    FeedListView,
    FeedCategoryListView,
    FeedDetailView,
    LikeView,
    FeedNotificationView,
    GroupPurchaseListView,
    GroupPurchaseJoinedUserView,
)

urlpatterns = [
    path("", CommunityView.as_view(), name="community_view"),
    path("<str:community_url>/feed/", include("feed.urls")),
    path(
        "<str:community_url>/",
        CommunityDetailView.as_view(),
        name="community_detail_view",
    ),
    path(
        "<str:community_url>/category/",
        CommunityCategoryView.as_view(),
        name="community_category_view",
    ),
    path(
        "<str:community_url>/subadmin/",
        CommunitySubAdminView.as_view(),
        name="community_subadmin_view",
    ),
    path(
        "<str:community_url>/forbidden/",
        CommunityForbiddenView.as_view(),
        name="community_forbidden_view",
    ),
    path(
        "<str:community_url>/forbidden/<str:forbidden_word>/",
        CommunityForbiddenView.as_view(),
        name="community_forbidden_view",
    ),
    path(
        "<str:community_url>/bookmark/",
        CommunityBookmarkView.as_view(),
        name="community_bookmark_view",
    ),
    path("search", SearchCommunityView.as_view(), name="search_community_view"),
    # feed 전체 list get
    path(
        "<str:community_url>/list/",
        FeedListView.as_view(),
        name="feed_list_view",
    ),
    # feed 카테고리 list get
    path(
        "<str:community_url>/category/<str:category_url>/",
        FeedCategoryListView.as_view(),
        name="feed_category_list_view",
    ),
    # feed 상세, 삭제 comment get
    path(
        "<str:community_url>/<int:feed_id>/",
        FeedDetailView.as_view(),
        name="feed_detail_view",
    ),
    # 이전 글, 다음 글
    path(
        "<str:community_url>/<int:feed_id>/prev/",
        FeedPrevView.as_view(),
        name="prev_feed",
    ),
    path(
        "<str:community_url>/<int:feed_id>/next/",
        FeedNextView.as_view(),
        name="next_feed",
    ),
    # like 설정/취소
    path("<int:feed_id>/likes/", LikeView.as_view(), name="like_view"),
    # feed 게시글 공지 설정/취소
    path(
        "<str:community_url>/<int:feed_id>/notification/",
        FeedNotificationView.as_view(),
        name="feed_notification_view",
    ),
    # grouppurchase 전체 list
    path(
        "<str:community_url>/grouppurchase/",
        GroupPurchaseListView.as_view(),
        name="grouppurchase_list_view",
    ),
    # grouppurchase 참여 / 취소
    path(
        "<int:grouppurchase_id>/join/",
        GroupPurchaseJoinedUserView.as_view(),
        name="grouppurchase_join_view",
    ),
]
