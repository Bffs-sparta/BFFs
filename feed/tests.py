from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from user.models import User
from feed.models import Feed, Category, Comment, Cocomment, GroupPurchase, JoinedUser
from community.models import Community, CommunityAdmin, ForbiddenWord


class FeedViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.community = Community.objects.create(
            title="title1", introduction="introduction1"
        )
        cls.category = Category.objects.create(
            community=cls.community, category_name="얘기해요"
        )
        cls.path = reverse("feed_list_view", kwargs={"community_name": "title1"})
        cls.category_path = reverse(
            "feed_category_list_view",
            kwargs={"community_name": "title1", "category_name": "얘기해요"},
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
        self.assertEqual(response.status_code, 204)


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
            title="title1", introduction="introduction1"
        )
        CommunityAdmin.objects.create(
            user=cls.user, community=cls.community, is_comuadmin=True
        )
        CommunityAdmin.objects.create(
            user=cls.user2, community=cls.community, is_subadmin=True
        )
        cls.category = Category.objects.create(
            community=cls.community, category_name="얘기해요"
        )
        cls.feed = Feed.objects.create(
            user=cls.user, category=cls.category, title="title1", content="content1"
        )
        cls.feed_data = {
            "category": 1,
            "title": "title1",
            "content": "content1",
        }
        cls.path = reverse(
            "feed_detail_view", kwargs={"community_name": "title1", "feed_id": 1}
        )
        cls.path2 = reverse("feed_detail_view", kwargs={"feed_id": 1})
        cls.path3 = reverse("feed_create_view", kwargs={"category_id": 1})
        cls.path4 = reverse("like_view", kwargs={"feed_id": 1})
        cls.path5 = reverse(
            "feed_notification_view", kwargs={"community_name": "title1", "feed_id": 1}
        )

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
                "feed_detail_view", kwargs={"community_name": "title1", "feed_id": 2}
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
            path=self.path2,
            data=self.feed_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)

    def test_put_feed_detail_success(self):
        """피드 수정 성공"""
        response = self.client.put(
            path=self.path2,
            data=self.feed_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_put_feed_detail_no_data(self):
        """data 없을 때 피드 수정 실패"""
        response = self.client.put(
            path=self.path2,
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
        """피드 삭제 작성자 아닐때"""
        response = self.client.delete(
            path=self.path2,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_feed_detail_success(self):
        """피드 삭제 성공"""
        response = self.client.delete(
            path=self.path2,
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
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_feed_detail_no_category(self):
        """category 없을 때 피드 생성 실패"""
        response = self.client.post(
            path=reverse("feed_create_view", kwargs={"category_name": 3}),
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
                kwargs={"community_name": "title1", "feed_id": 10},
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
        print(response.data)
        self.assertEqual(response.data["data"]["is_notification"], True)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(
            path=self.path5,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        print(response.data)
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
            title="title1", introduction="introduction1"
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
