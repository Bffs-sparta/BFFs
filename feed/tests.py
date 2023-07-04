from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status

from user.models import User, Profile
from feed.models import (
    Feed,
    Category,
    Comment,
    Cocomment,
    GroupPurchase,
    JoinedUser,
    GroupPurchaseComment,
)
from community.models import Community, CommunityAdmin, ForbiddenWord


class FeedViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.community = Community.objects.create(
            title="title1", communityurl="title1", introduction="introduction1"
        )
        cls.category = Category.objects.create(
            community=cls.community, category_name="얘기해요", category_url="talk"
        )
        cls.path = reverse("feed_list_view", kwargs={"community_url": "title1"})
        cls.category_path = reverse(
            "feed_category_list_view",
            kwargs={"community_url": "title1", "category_url": "talk"},
        )

    def test_get_all_feed_list(self):
        """피드 전체 리스트 조회"""
        Feed.objects.create(
            user=self.user, category=self.category, title="title1", content="content1"
        )

        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_no_feed_list(self):
        """피드 게시글 없을 때"""
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 204)

    def test_get_all_feed_category_list(self):
        """피드 카테고리 리스트 조회"""
        Feed.objects.create(
            user=self.user, category=self.category, title="title1", content="content1"
        )

        response = self.client.get(
            path=self.category_path,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_no_feed_category_list(self):
        """피드 카테고리 게시글 없을 때"""
        response = self.client.get(
            path=self.category_path,
        )
        self.assertEqual(response.status_code, 200)


class FeedDetailViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test1@naver.com",
            "name": "test1",
            "password": "test123!",
        }
        cls.user_data2 = {
            "email": "test2@naver.com",
            "name": "test2",
            "password": "test123!",
        }
        cls.user_data3 = {
            "email": "test3@naver.com",
            "name": "test3",
            "password": "test123!",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.user2 = User.objects.create_user(**cls.user_data2)
        cls.user3 = User.objects.create_user(**cls.user_data3)
        cls.community = Community.objects.create(
            title="title1", communityurl="title1", introduction="introduction1"
        )
        CommunityAdmin.objects.create(
            user=cls.user, community=cls.community, is_comuadmin=True
        )
        CommunityAdmin.objects.create(
            user=cls.user2, community=cls.community, is_subadmin=True
        )
        cls.category = Category.objects.create(
            community=cls.community,
            id=1,
            category_name="얘기해요",
            category_url="talk",
        )
        cls.feed = Feed.objects.create(
            user=cls.user, category=cls.category, title="title1", content="content1"
        )
        cls.feed_data = {
            "category_id": 1,
            "title": "title1",
            "content": "content1",
        }
        cls.path = reverse(
            "feed_detail_view", kwargs={"community_url": "title1", "feed_id": 1}
        )
        cls.path2 = reverse("feed_detail_view", kwargs={"feed_id": 1})
        cls.path3 = reverse("feed_create_view", kwargs={"community_url": "title1"})
        cls.path4 = reverse("like_view", kwargs={"feed_id": 1})
        cls.path5 = reverse("feed_notification_view", kwargs={"feed_id": 1})

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data.get(
            "access"
        )
        self.access_token2 = self.client.post(
            reverse("login"), self.user_data2
        ).data.get("access")
        self.access_token3 = self.client.post(
            reverse("login"), self.user_data3
        ).data.get("access")

    def test_get_feed_detail(self):
        """피드 디테일 조회 실패"""
        response = self.client.get(
            path=reverse(
                "feed_detail_view", kwargs={"community_url": "title1", "feed_id": 2}
            )
        )
        self.assertEqual(response.status_code, 404)

    def test_get_feed_detail_no_comment(self):
        """피드 디테일 조회 댓글 없음"""
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.data["comment"], "아직 댓글이 없습니다")

    def test_get_feed_detail_no_comment_countup(self):
        """피드 디테일 조회 댓글 없음 조회수 +1"""
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.data["feed"]["view_count"], 1)

    def test_get_feed_detail_exist_comment(self):
        """피드 디테일 조회 댓글 있음"""
        Comment.objects.create(user=self.user, feed=self.feed, text="comment1")

        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 200)

    def test_get_feed_detail_exist_comment_countup(self):
        """피드 디테일 조회 댓글 있음 조회수 +1"""
        Comment.objects.create(user=self.user, feed=self.feed, text="comment1")

        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.data["feed"]["view_count"], 1)

    def test_put_feed_detail_if_not_logged_in(self):
        """피드 수정시 로그인 확인"""
        response = self.client.put(
            path=self.path,
            data=self.feed_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_put_feed_detail_not_user(self):
        """피드 수정 작성자 아닐때"""
        response = self.client.put(
            path=self.path,
            data=self.feed_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)

    def test_put_feed_detail_success(self):
        """피드 수정 성공"""
        response = self.client.put(
            path=self.path,
            data=self.feed_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_put_feed_detail_no_data(self):
        """data 없을 때 피드 수정 실패"""
        response = self.client.put(
            path=self.path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_feed_detail_if_not_logged_in(self):
        """피드 삭제시 로그인 확인"""
        response = self.client.delete(
            path=self.path2,
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_feed_detail_not_user(self):
        """피드 삭제 작성자 아니고 서브어드민일 때 삭제 성공"""
        response = self.client.delete(
            path=self.path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_feed_detail_success(self):
        """피드 삭제 성공"""
        response = self.client.delete(
            path=self.path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_post_feed_detail_if_not_logged_in(self):
        """피드 생성시 로그인 확인"""
        response = self.client.post(
            path=self.path3,
            data=self.feed_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_post_feed_detail_no_data(self):
        """data 없을 때 피드 생성 실패"""
        response = self.client.post(
            path=self.path3,
            data={"category_id": 1},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_feed_detail_no_category(self):
        """category 없을 때 피드 생성 실패"""
        response = self.client.post(
            path=self.path3,
            data={
                "category_id": 2,
                "title": "title1",
                "content": "content1",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_feed_detail_success(self):
        """피드 생성 성공"""
        response = self.client.post(
            path=self.path3,
            data=self.feed_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_post_feed_like_if_not_logged_in(self):
        """feed 좋아요시 로그인 확인"""
        response = self.client.post(
            path=self.path4,
        )
        self.assertEqual(response.status_code, 401)

    def test_post_feed_like_no_category(self):
        """feed 없을 때 좋아요 실패"""
        response = self.client.post(
            path=reverse("like_view", kwargs={"feed_id": 2}),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_feed_like_success(self):
        """feed 좋아요 성공"""
        response = self.client.post(
            path=self.path4,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_post_feed_unlike_success(self):
        """feed 좋아요 취소 성공"""
        feed = Feed.objects.get(id=1)
        feed.likes.add(self.user)
        response = self.client.post(
            path=self.path4,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.data, "좋아요를 취소했습니다.")

    def test_post_feed_notification_if_not_logged_in(self):
        """공지글 등록시 로그인 확인"""
        response = self.client.post(
            path=self.path5,
        )
        self.assertEqual(response.status_code, 401)

    def test_post_feed_notification_no_feed(self):
        """feed 없을 때 공지 실패"""
        response = self.client.post(
            path=reverse(
                "feed_notification_view",
                kwargs={"feed_id": 10},
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 404)

    def test_post_feed_notification_no_admin(self):
        """관리자 아닐 때 공지 실패"""
        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token3}",
        )
        self.assertEqual(response.status_code, 403)

    def test_post_feed_notification_success1(self):
        """관리자일 때 공지 성공"""
        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.data["data"]["is_notification"], True)
        self.assertEqual(response.status_code, 200)

    def test_post_feed_notification_success2(self):
        """서브관리자일 때 공지 성공"""
        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.data["data"]["is_notification"], True)
        self.assertEqual(response.status_code, 200)

    def test_post_feed_notification_success3(self):
        """관리자일 때 공지글 설정 및 취소"""
        Feed.objects.get(id=1)

        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.data["data"]["is_notification"], True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.data["data"]["is_notification"], False)
        self.assertEqual(response.status_code, 200)

    def test_post_feed_notification_success4(self):
        """이미 공지글일 때 & 서브관리자일 때 공지 취소 성공"""
        Feed.objects.get(id=1)

        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.data["data"]["is_notification"], True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.data["data"]["is_notification"], False)
        self.assertEqual(response.status_code, 200)


class CommentTestView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test1@naver.com",
            "name": "test1",
            "password": "test123!",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.user2_data = {
            "email": "test2@naver.com",
            "name": "test2",
            "password": "test123!",
        }
        cls.user2 = User.objects.create_user(**cls.user2_data)
        cls.community = Community.objects.create(
            title="title1", communityurl="title1", introduction="introduction1"
        )
        cls.category = Category.objects.create(
            community=cls.community, category_name="얘기해요"
        )
        cls.feed = Feed.objects.create(
            user=cls.user, category=cls.category, title="title1", content="content1"
        )
        cls.path = reverse("comment_create_view", kwargs={"feed_id": 1})
        cls.comment_path = reverse("comment_put_delete_view", kwargs={"comment_id": 1})
        cls.comment = Comment.objects.create(
            feed=cls.feed, user=cls.user, text="comment1"
        )

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data.get(
            "access"
        )
        self.access_token2 = self.client.post(
            reverse("login"), self.user2_data
        ).data.get("access")

    def test_comment_create(self):
        """댓글 생성"""
        response = self.client.post(
            path=self.path,
            data={
                "feed": self.feed,
                "text": "comment1",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_comment_create_not_user(self):
        """댓글 생성"""
        response = self.client.post(
            path=self.path,
            data={
                "feed": self.feed,
                "text": "comment1",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_comment_create_not_include_text(self):
        """댓글 생성"""
        response = self.client.post(
            path=self.path,
            data={
                "feed": self.feed,
                "text": "",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_comment_put(self):
        response = self.client.put(
            path=self.comment_path,
            data={
                "text": "comment2",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 200)

    def test_comment_put_not_user(self):
        response = self.client.put(
            path=self.comment_path,
            data={
                "text": "comment2",
            },
        )

        self.assertEqual(response.status_code, 401)

    def test_comment_put_not_include_test(self):
        response = self.client.put(
            path=self.comment_path,
            data={
                "text": "",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_comment_put_notMatch_user(self):
        response = self.client.put(
            path=self.comment_path,
            data={
                "text": "comment2",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)

    def test_comment_delete(self):
        response = self.client.delete(
            path=self.comment_path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_comment_delete_not_user(self):
        response = self.client.delete(
            path=self.comment_path,
        )
        self.assertEqual(response.status_code, 401)

    def test_comment_delelte_notMatch_user(self):
        response = self.client.delete(
            path=self.comment_path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)


class CocommentViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test1@naver.com",
            "name": "test1",
            "password": "test123!",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.user2_data = {
            "email": "test2@naver.com",
            "name": "test2",
            "password": "test123!",
        }
        cls.user2 = User.objects.create_user(**cls.user2_data)
        cls.community = Community.objects.create(
            title="title1", introduction="introduction1"
        )
        cls.category = Category.objects.create(
            community=cls.community, category_name="얘기해요"
        )
        cls.feed = Feed.objects.create(
            user=cls.user, category=cls.category, title="title1", content="content1"
        )
        cls.comment = Comment.objects.create(
            feed=cls.feed, user=cls.user, text="comment1"
        )
        cls.cocomment = Cocomment.objects.create(
            comment=cls.comment, user=cls.user, text="cocoment1"
        )

        cls.path = reverse("cocomment_create_view", kwargs={"comment_id": 1})
        cls.cocomment_path = reverse(
            "cocomment_put_delete_view", kwargs={"cocomment_id": 1}
        )

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data.get(
            "access"
        )
        self.access_token2 = self.client.post(
            reverse("login"), self.user2_data
        ).data.get("access")

    def test_cocomment_create(self):
        response = self.client.post(
            path=self.path,
            data={
                "text": "cocomment2",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_cocomment_create_not_user(self):
        response = self.client.post(
            path=self.path,
            data={
                "text": "cocomment2",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_cocomment_create_not_test(self):
        response = self.client.post(
            path=self.path,
            data={
                "text": "",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_cocomment_put_not_user(self):
        response = self.client.put(
            path=self.cocomment_path,
            data={
                "text": "cocomment2",
            },
        )
        self.assertEqual(response.status_code, 401)

    def test_cocomment_put_notMatch_user(self):
        response = self.client.put(
            path=self.cocomment_path,
            data={
                "text": "cocomment2",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)

    def test_cocomment_put_not_text(self):
        response = self.client.put(
            path=self.cocomment_path,
            data={
                "text": "",
            },
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )

        self.assertEqual(response.status_code, 400)

    def test_cocomment_delete(self):
        response = self.client.delete(
            path=self.cocomment_path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_cocomment_delete_not_user(self):
        response = self.client.delete(
            path=self.cocomment_path,
        )
        self.assertEqual(response.status_code, 401)

    def test_cocomment_delete_notMatch_user(self):
        response = self.client.delete(
            path=self.cocomment_path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)


# class GroupPurchaseViewTest(APITestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.client = APIClient()
#         cls.user_data = {
#             "email": "test01@test.com",
#             "name": "test01",
#             "password": "test12!@",
#         }
#         cls.user_data2 = {
#             "email": "test02@test.com",
#             "name": "test02",
#             "password": "test12!@",
#         }
#         cls.user_data3 = {
#             "email": "test03@test.com",
#             "name": "test03",
#             "password": "test12!@",
#         }

#         cls.user = User.objects.create_user("test01@test.com", "test01", "test12!@")
#         cls.user2 = User.objects.create_user("test02@test.com", "test02", "test12!@")
#         cls.user3 = User.objects.create_user("test03@test.com", "test03", "test12!@")
#         cls.profile_data = {
#             "user": cls.user,
#             "nickname": "nicktest1",
#             "introduction": "introduction test",
#             "region": "seoul",
#         }
#         cls.profile_data2 = {
#             "user": cls.user2,
#             "nickname": "nicktest1",
#             "introduction": "introduction test",
#             "region": "seoul",
#         }
#         cls.user_profile = Profile.objects.update(nickname="nickname1")
#         cls.user_profile = Profile.objects.update(region="seoul")
#         cls.user2_profile = Profile.objects.update(nickname="nickname2")
#         cls.user2_profile = Profile.objects.update(region="seoul")

#         cls.access_token = cls.client.post(reverse("login"), cls.user_data).data[
#             "access"
#         ]
#         cls.access_token2 = cls.client.post(reverse("login"), cls.user_data2).data[
#             "access"
#         ]
#         cls.access_token3 = cls.client.post(reverse("login"), cls.user_data3).data[
#             "access"
#         ]

#         cls.community_data = {
#             "title": "community1",
#             "communityurl": "community1",
#             "introduction": "introduction1",
#         }
#         cls.community = Community.objects.create(
#             title="community1", communityurl="community1", introduction="introduction1"
#         )
#         CommunityAdmin.objects.create(
#             user=cls.user, community=cls.community, is_comuadmin=True
#         )
#         cls.category_data = {
#             "id": 3,
#             "community": cls.community,
#             "category_name": "공구해요",
#             "category_url": "groupbuy",
#         }
#         cls.category = Category.objects.create(
#             id=3,
#             community=cls.community,
#             category_name="공구해요",
#             category_url="groupbuy",
#         )

#         cls.grouppurchase = GroupPurchase.objects.create(
#             community=cls.community,
#             category=cls.category,
#             user=cls.user,
#             title="puchase create feed3",
#             content="purchase test feed create",
#             product_name="상품명",
#             product_number="2",
#             product_price="10000",
#             link="https://diane073.tistory.com/",
#             person_limit="2",
#             location="서울시 송파구, 석촌역 8번출구 앞",
#             meeting_at="2023-06-21T12:00:00",
#             open_at="2023-06-20T18:00:00",
#             close_at="2023-06-21T09:00:00",
#             end_option="quit",
#         )
#         cls.grouppurchase_limit_10 = GroupPurchase.objects.create(
#             community=cls.community,
#             category=cls.category,
#             user=cls.user,
#             title="puchase create feed3",
#             content="purchase test feed create",
#             product_name="상품명",
#             product_number="2",
#             product_price="10000",
#             link="https://diane073.tistory.com/",
#             person_limit="10",
#             location="서울시 송파구, 석촌역 8번출구 앞",
#             meeting_at="2023-06-21T12:00:00",
#             open_at="2023-06-20T18:00:00",
#             close_at="2023-06-21T09:00:00",
#             end_option="quit",
#         )
#         cls.grouppurchase_limit_1 = GroupPurchase.objects.create(
#             community=cls.community,
#             category=cls.category,
#             user=cls.user,
#             title="puchase create feed3",
#             content="purchase test feed create",
#             product_name="상품명",
#             product_number="2",
#             product_price="10000",
#             link="https://diane073.tistory.com/",
#             person_limit="1",
#             location="서울시 송파구, 석촌역 8번출구 앞",
#             meeting_at="2023-06-21T12:00:00",
#             open_at="2023-06-20T18:00:00",
#             close_at="2023-06-21T09:00:00",
#             end_option="quit",
#         )
#         cls.grouppurchase_is_ended = GroupPurchase.objects.create(
#             community=cls.community,
#             category=cls.category,
#             user=cls.user,
#             title="puchase create feed3",
#             content="purchase test feed create",
#             product_name="상품명",
#             product_number="10",
#             product_price="10000",
#             link="https://diane073.tistory.com/",
#             person_limit="2",
#             location="서울시 송파구, 석촌역 8번출구 앞",
#             meeting_at="2023-06-09T12:00:00",
#             open_at="2023-06-10T18:00:00",
#             close_at="2023-06-11T09:00:00",
#             end_option="quit",
#             is_ended="True",
#         )
#         cls.joined_user = JoinedUser.objects.create(
#             grouppurchase=cls.grouppurchase_limit_10, user=cls.user, product_quantity=1
#         )
#         cls.quit_user = JoinedUser.objects.create(
#             grouppurchase=cls.grouppurchase_limit_10,
#             user=cls.user,
#             product_quantity=0,
#             is_deleted=True,
#         )

#         cls.purchase_comment = GroupPurchaseComment.objects.create(
#             grouppurchase=cls.grouppurchase, user=cls.user, text="test comment1"
#         )

#         cls.path = reverse(
#             "grouppurchase_create_view", args=[cls.community.communityurl]
#         )
#         cls.path2 = reverse(
#             "grouppurchase_put_delete_view",
#             args=[cls.community.communityurl, cls.grouppurchase.id],
#         )
#         cls.path3 = reverse(
#             "grouppurchase_put_delete_view",
#             args=[cls.community.communityurl, cls.grouppurchase_is_ended.id],
#         )
#         cls.path4 = reverse(
#             "grouppurchase_list_view", args=[cls.community.communityurl]
#         )
#         cls.path5 = reverse(
#             "grouppurchase_put_delete_view",
#             args=[cls.community.communityurl, cls.grouppurchase.id],
#         )
#         cls.path6 = reverse("grouppurchase_join_view", args=[cls.grouppurchase.id])
#         cls.path7 = reverse(
#             "grouppurchase_join_view", args=[cls.grouppurchase_limit_1.id]
#         )
#         cls.path8 = reverse(
#             "grouppurchase_join_view", args=[cls.grouppurchase_is_ended.id]
#         )
#         cls.path9 = reverse(
#             "grouppurchase_join_view", args=[cls.grouppurchase_limit_10.id]
#         )
#         cls.path10 = reverse(
#             "purchase_comment_create_view", args=[cls.grouppurchase.id]
#         )
#         cls.path11 = reverse(
#             "purchase_comment_put_delete_view", args=[cls.purchase_comment.id]
#         )

#     def setUp(self):
#         self.grouppurchase_data = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed3",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2099-07-31T12:00:00",
#             "open_at": "2025-07-20T18:00:00",
#             "close_at": "2099-07-23T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_open_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "9999-06-30T12:00:00",
#             "open_at": "2023-06-01T18:00:00",
#             "close_at": "9999-06-25T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_close_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "5",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "9999-06-30T12:00:00",
#             "open_at": "9999-06-25T18:00:00",
#             "close_at": "2023-06-10T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_meeting_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-06-10T12:00:00",
#             "open_at": "9999-06-25T18:00:00",
#             "close_at": "9999-06-30T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_not_close_open_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "9999-06-30T12:00:00",
#             "open_at": "2023-06-01T18:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_not_close_meeting_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-06-10T12:00:00",
#             "open_at": "9999-06-25T18:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_not_close_open_meeting_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-06-10T12:00:00",
#             "open_at": "9999-06-25T18:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_not_close_now_meeting_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-07-1T12:00:00",
#             "open_at": "2023-06-25T18:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_data_is_ended = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase create feed",
#             "content": "purchase test feed create",
#             "product_name": "상품명",
#             "product_number": "10",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-06-01T12:00:00",
#             "open_at": "2023-06-01T18:00:00",
#             "close_at": "2023-06-10T09:00:00",
#             "end_option": "quit",
#             "is_ended": "True",
#         }
#         self.grouppurchase_update_data = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase update",
#             "content": "purchase update",
#             "product_name": "product",
#             "product_number": "2",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "9999-06-30T12:00:00",
#             "open_at": "9999-06-24T18:00:00",
#             "close_at": "9999-06-25T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_update_data_meeting_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase update",
#             "content": "purchase update",
#             "product_name": "product",
#             "product_number": "2",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "2023-06-10T12:00:00",
#             "open_at": "9999-06-24T18:00:00",
#             "close_at": "9999-06-30T09:00:00",
#             "end_option": "quit",
#         }
#         self.grouppurchase_update_data_close_fail = {
#             "community": self.community.id,
#             "category": self.category.id,
#             "user": self.user.id,
#             "title": "purchase update",
#             "content": "purchase update",
#             "product_name": "product",
#             "product_number": "2",
#             "product_price": "10000",
#             "link": "https://diane073.tistory.com/",
#             "person_limit": "2",
#             "location": "서울시 송파구, 석촌역 8번출구 앞",
#             "meeting_at": "9999-06-30T12:00:00",
#             "open_at": "9999-06-24T18:00:00",
#             "close_at": "2023-06-10T09:00:00",
#             "end_option": "quit",
#         }
#         self.join_data = {"product_quantity": 1}
#         self.join_data_update = {"product_quantity": 2}
#         self.join_data_0 = {"product_quantity": 0}
#         self.join_data_1 = {"product_quantity": -1}
#         self.purchase_comment_data = {
#             "grouppurchase": self.grouppurchase,
#             "text": "test comment1",
#         }
#         self.purchase_comment_data2 = {
#             "grouppurchase": self.grouppurchase,
#             "text": "test update comment1",
#         }

#     def test_create_grouppurchase_feed(self):
#         """공구 게시글 생성 성공"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 201)

#     def test_create_grouppurchase_feed_open_fail(self):
#         """공구 게시글 open 시간이 현재시간보다 느리게 생성"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data_open_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(str(response.data["error"]), "모집 시작시간 오류. 현재 이후의 시점을 선택해주세요.")
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_close_fail(self):
#         """공구 게시글 close 시간이 open 시간보다 느리게 생성"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data_close_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "모집 종료시간 오류. 모집 시작보다 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_meeting_fail(self):
#         """공구 게시글 meeting 시간이 close 시간보다 느리게 생성"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data_meeting_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "만날시간 오류. 모집 종료보다 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_not_close_open_fail(self):
#         """not close_at / 공구 게시글 open 시간이 현재시간보다 느리게 생성"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data_not_close_open_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "모집 시작시간 오류. 현재 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_not_close_meeting_fail(self):
#         """not close_at / 공구 게시글 meeting 시간이 open 시간보다 느리게 생성"""
#         response = self.client.post(
#             path=self.path,
#             data=self.grouppurchase_data_not_close_meeting_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "만날시간 오류. 모집 시작보다 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_update_grouppurchase_feed(self):
#         """공구 게시글 수정 성공"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_update_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_update_grouppurchase_feed_not_matched_user(self):
#         """공구 게시글 권한없는 유저 수정 실패"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_update_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_update_grouppurchase_feed_close_fail(self):
#         """공구 게시글 수정 실패, close시간"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_update_data_close_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "모집 종료시간 오류. 현재 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_update_grouppurchase_feed_meeting_fail(self):
#         """공구 게시글 수정 실패, meeting시간"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_update_data_meeting_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "만날시간 오류. 모집 종료보다 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_not_close_meeting_fail_1(self):
#         """not close_at / 현재 > meeting시간 실패"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_data_not_close_now_meeting_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.data["error"].title(), "만날시간 오류. 현재 이후의 시점을 선택해주세요.")
#         self.assertEqual(response.status_code, 400)

#     def test_create_grouppurchase_feed_not_close_meeting_fail_2(self):
#         """not close_at / open > meeting 실패"""
#         response = self.client.put(
#             path=self.path2,
#             data=self.grouppurchase_data_not_close_open_meeting_fail,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(
#             response.data["error"].title(), "만날시간 오류. 모집 시작보다 이후의 시점을 선택해주세요."
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_delete_grouppurchase_feed_not_matched_user(self):
#         """공구 게시글 권한없는 유저 삭제 실패"""
#         response = self.client.delete(
#             self.path2, HTTP_AUTHORIZATION=f"Bearer {self.access_token2}"
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_delete_grouppurchase_feed(self):
#         """공구 게시글 삭제"""
#         response = self.client.delete(
#             self.path2, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_delete_grouppurchase_feed_not_matched_user(self):
#         """공구 게시글 권한없는 유저 삭제 실패"""
#         response = self.client.delete(
#             self.path2, HTTP_AUTHORIZATION=f"Bearer {self.access_token2}"
#         )
#         self.assertEqual(response.status_code, 403)

#     def test_delete_grouppurchase_feed_endned_fail(self):
#         """종료된 공구 게시글 삭제 실패"""
#         response = self.client.delete(
#             self.path3, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
#         )
#         self.assertEqual(response.status_code, 405)

#     def test_get_grouppurchase_feed_list(self):
#         """공구 게시글 list get, 로그인 없이"""
#         response = self.client.get(
#             path=self.path4,
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_get_grouppurchase_feed_detail(self):
#         """공구 게시글 상세 get, 로그인 없이"""
#         response = self.client.get(
#             path=self.path5,
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_get_grouppurchase_detail_fail(self):
#         """공구 게시글 상세 조회 실패"""
#         response = self.client.get(
#             path=reverse(
#                 "grouppurchase_put_delete_view",
#                 kwargs={
#                     "community_url": self.community.communityurl,
#                     "grouppurchase_id": 100,
#                 },
#             )
#         )
#         self.assertEqual(response.status_code, 404)

#     def test_get_feed_detail_check_view_count(self):
#         """공구 게시글 상세 조회 시 조회수 +1"""
#         response = self.client.get(
#             path=self.path5,
#         )
#         self.assertEqual(response.data["grouppurchase"]["view_count"], 1)

#     def test_post_grouppurchase_join_success(self):
#         """공구 게시글 참여 성공"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response.status_code, 201)

#     def test_post_grouppurchase_join_update(self):
#         """공구 게시글 참여 성공 후 수량 조절"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )

#         response2 = self.client.post(
#             path=self.path6,
#             data=self.join_data_update,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response2.data["message"], "공구 수량을 수정했습니다.")
#         self.assertEqual(response2.data["data"]["product_quantity"], 2)
#         self.assertEqual(response2.status_code, 202)

#     def test_post_grouppurchase_join_update_zero(self):
#         """공구 게시글 참여 실패, 수량 0"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data_0,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_post_grouppurchase_join_update_minus(self):
#         """공구 게시글 참여 실패, 수량 -1"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data_1,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response.data["message"], "수량을 다시 확인해주세요.")
#         self.assertEqual(response.status_code, 400)

#     def test_post_grouppurchase_limit(self):
#         """공구 게시글 참여 limit 1명, 종료"""
#         response = self.client.post(
#             path=self.path7,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 201)

#         # user2 참여
#         response = self.client.post(
#             path=self.path7,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response.data["message"], "공구 인원이 모두 찼습니다!")
#         self.assertEqual(response.status_code, 405)

#     def test_post_grouppurchase_ended_join(self):
#         """공구 게시글 모집 완료된 게시글에 참여 실패"""
#         response = self.client.post(
#             path=self.path8,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_post_grouppurchase_join_quit(self):
#         """공구 게시글 참여 후 참여 취소"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )

#         response2 = self.client.post(
#             path=self.path6,
#             data=self.join_data_0,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response2.data["message"], "공구 신청을 취소했습니다.")
#         self.assertEqual(response2.status_code, 202)

#     def test_post_grouppurchase_re_join(self):
#         """공구 게시글 참여 취소 후 재참여"""
#         response = self.client.post(
#             path=self.path6,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )

#         response2 = self.client.post(
#             path=self.path6,
#             data=self.join_data_0,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )

#         response3 = self.client.post(
#             path=self.path6,
#             data=self.join_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
#         )
#         self.assertEqual(response3.data["message"], "공구를 재 신청했습니다.")
#         self.assertEqual(response3.status_code, 202)

#     # comment CRD test
#     def test_create_grouppurchase_comment(self):
#         """공구 게시글 comment 생성"""
#         response = self.client.post(
#             path=self.path10,
#             data=self.purchase_comment_data,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 201)

#     def test_create_comment_no_user(self):
#         """공구 댓글 수정 시 user 없음"""
#         response = self.client.post(path=self.path10, data=self.purchase_comment_data2)
#         self.assertEqual(response.status_code, 401)

#     def test_update_grouppurchase_comment(self):
#         """공구 게시글 comment 수정"""
#         response = self.client.put(
#             path=self.path11,
#             data=self.purchase_comment_data2,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.data["message"], "공구 댓글을 수정했습니다.")
#         self.assertEqual(response.status_code, 200)

#     def test_update_comment_no_user(self):
#         response = self.client.put(path=self.path10, data=self.purchase_comment_data2)
#         self.assertEqual(response.status_code, 401)

#     def test_update_grouppurchase_comment_no_text(self):
#         """공구 댓글 수정 시 text 없음"""
#         response = self.client.put(
#             path=self.path11,
#             data={
#                 "text": "",
#             },
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 400)

#     def test_update_grouppurchase_comment_not_matched_user(self):
#         """공구 게시글 comment 수정 실패, 권한없는 유저"""
#         response = self.client.put(
#             path=self.path11,
#             data=self.purchase_comment_data2,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token3}",
#         )
#         self.assertEqual(response.status_code, 403)

#     def test_delete_comment(self):
#         """공구 게시글 comment 삭제"""
#         response = self.client.delete(
#             path=self.path11,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
#         )
#         self.assertEqual(response.status_code, 200)

#     def test_delete_comment_no_user(self):
#         """공구 게시글 comment 삭제, 미 로그인 시"""
#         response = self.client.delete(
#             path=self.path11,
#         )
#         self.assertEqual(response.status_code, 401)

#     def test_delete_comment_not_matched_user(self):
#         """공구 게시글 comment 삭제, 권한없는 유저"""
#         response = self.client.delete(
#             path=self.path11,
#             HTTP_AUTHORIZATION=f"Bearer {self.access_token3}",
#         )
#         self.assertEqual(response.status_code, 403)
