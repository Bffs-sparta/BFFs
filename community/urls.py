from django.urls import path
from . import views

urlpatterns = [
    path("", views.CommunityView.as_view(), name="community"),
    path("<int:comu_id>/", views.CommunityView.as_view(), name="community_detail_view"),
    path("<int:comu_id>/subadmin/", views.CommunitySubAdminView.as_view(), name="community_subadmin_view"),
    path("<int:comu_id>/forbidden/", views.CommunityForbiddenView.as_view(), name="community_forbidden_view"),
    path("<int:comu_id>/bookmark/", views.CommunityBookmarkView.as_view(), name="community_bookmark_view"),
]
