from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from user.models import User
from community.models import Community, CommunityAdmin, ForbiddenWord


class CommunityViewTest(APITestCase):
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
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.user2 = User.objects.create_user("test2@naver.com", "test2", "test123!")
        cls.community_data = {"title": "title1", "introduction": "introduction1"}
        cls.community_edit_data = {"introduction": "introduction1"}
        cls.community = Community.objects.create(
            title="title2", introduction="introduction2"
        )
        CommunityAdmin.objects.create(
            user=cls.user, community=cls.community, is_comuadmin=True
        )
        cls.path = reverse("community_view")
        cls.path_name = reverse(
            "community_detail_view", kwargs={"community_name": "title2"}
        )

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]
        self.access_token2 = self.client.post(reverse("login"), self.user_data2).data[
            "access"
        ]

    def test_get_community(self):
        """커뮤니티 조회"""
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 200)

    def test_fail_if_not_logged_in(self):
        """커뮤니티 생성시 로그인 확인"""
        response = self.client.post(self.path, self.community_data)
        self.assertEqual(response.status_code, 401)

    def test_post_community_unique_name(self):
        """커뮤니티 생성시 unique title 확인"""
        Community.objects.create(title="title1", introduction="introduction1")

        response = self.client.post(
            path=self.path,
            data=self.community_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_community(self):
        """커뮤니티 생성 성공"""
        response = self.client.post(
            path=self.path,
            data=self.community_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 202)

    def test_post_community_create_comuadmin(self):
        """커뮤니티 생성시 comuadmin 생성 확인"""
        response = self.client.post(
            path=self.path,
            data=self.community_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        comu_id = response.data["data"].get("id")
        user_id = CommunityAdmin.objects.get(community_id=comu_id).user_id
        self.assertEqual(user_id, self.user.id)

    def test_put_community_unauthorized(self):
        """비로그인시 커뮤니티 수정 권한 없음"""
        response = self.client.put(
            path=self.path_name,
            data=self.community_edit_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_put_community_no_admin(self):
        """admin 아닐때 커뮤니티 수정 실패"""
        response = self.client.put(
            path=self.path_name, HTTP_AUTHORIZATION=f"Bearer {self.access_token2}"
        )
        self.assertEqual(response.status_code, 401)

    def test_put_community(self):
        """커뮤니티 수정 성공"""
        response = self.client.put(
            path=self.path_name,
            data=self.community_edit_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_community_unauthorized(self):
        """비로그인시 커뮤니티 삭제 권한 없음"""
        response = self.client.delete(
            path=self.path_name,
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_community_no_admin(self):
        """admin 아닐때 커뮤니티 삭제 실패"""
        response = self.client.delete(
            path=self.path_name, HTTP_AUTHORIZATION=f"Bearer {self.access_token2}"
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_community(self):
        """커뮤니티 삭제 성공"""
        response = self.client.delete(
            path=self.path_name, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 204)


class CommunitySubAdminViewTest(APITestCase):
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
        cls.user_data4 = {
            "email": "test4@naver.com",
            "name": "test4",
            "password": "test123!",
        }
        cls.user_data5 = {
            "email": "test5@naver.com",
            "name": "test5",
            "password": "test123!",
        }
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.user2 = User.objects.create_user("test2@naver.com", "test2", "test123!")
        cls.user3 = User.objects.create_user("test3@naver.com", "test3", "test123!")
        cls.user4 = User.objects.create_user("test4@naver.com", "test4", "test123!")
        cls.user5 = User.objects.create_user("test5@naver.com", "test5", "test123!")
        cls.community = Community.objects.create(
            title="title1", introduction="introduction1"
        )
        CommunityAdmin.objects.create(
            user=cls.user, community=cls.community, is_comuadmin=True
        )
        CommunityAdmin.objects.create(
            user=cls.user2, community=cls.community, is_subadmin=True
        )
        cls.path = reverse(
            "community_subadmin_view", kwargs={"community_name": "title1"}
        )
        cls.exist_subadmin_data = {"user": 2}

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]
        self.access_token2 = self.client.post(reverse("login"), self.user_data2).data[
            "access"
        ]

    def test_post_subadmin_fail_if_not_logged_in(self):
        """sub admin 생성시 로그인 확인"""
        response = self.client.post(
            path=self.path,
            data={"user": 3},
        )
        self.assertEqual(response.status_code, 401)

    def test_post_subadmin_no_admin(self):
        """admin 아닐때 sub admin 생성 실패"""
        response = self.client.post(
            path=self.path,
            data={"user": 3},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 401)

    def test_post_subadmin_exist_subadmin(self):
        """이미 sub admin일 때 sub admin 생성 실패"""
        response = self.client.post(
            path=self.path,
            data=self.exist_subadmin_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_max_subadmin(self):
        """이미 sub admin이 3명일 때 sub admin 생성 실패"""
        CommunityAdmin.objects.create(
            user=self.user3, community=self.community, is_subadmin=True
        )
        CommunityAdmin.objects.create(
            user=self.user4, community=self.community, is_subadmin=True
        )

        response = self.client.post(
            path=self.path,
            data={"user": 5},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_subadmin(self):
        """sub admin 생성 성공"""
        response = self.client.post(
            path=self.path,
            data={"user": 3},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_delete_subadmin_unauthorized(self):
        """비로그인시 sub admin 삭제 권한 없음"""
        response = self.client.delete(
            path=self.path,
            data=self.exist_subadmin_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_subadmin_no_admin(self):
        """admin 아닐 때 sub admin 삭제 실패"""
        response = self.client.delete(
            path=self.path,
            data=self.exist_subadmin_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 401)

    def test_delete_no_subadmin(self):
        """존재하지 않는 sub admin 삭제 실패"""
        response = self.client.delete(
            path=self.path,
            data={"user": 3},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_subadmin(self):
        """sub admin 삭제 성공"""
        response = self.client.delete(
            path=self.path,
            data=self.exist_subadmin_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)


class CommunityForbiddenViewTest(APITestCase):
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
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.user2 = User.objects.create_user("test2@naver.com", "test2", "test123!")
        cls.community = Community.objects.create(
            title="title1", introduction="introduction1"
        )
        CommunityAdmin.objects.create(
            user=cls.user, community=cls.community, is_comuadmin=True
        )
        CommunityAdmin.objects.create(
            user=cls.user2, community=cls.community, is_subadmin=True
        )
        cls.path = reverse(
            "community_forbidden_view", kwargs={"community_name": "title1"}
        )
        cls.word_data = {"word": "word"}
        ForbiddenWord.objects.create(word="word2", community=cls.community)

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]
        self.access_token2 = self.client.post(reverse("login"), self.user_data2).data[
            "access"
        ]

    def test_get_forbiddenword(self):
        """금지어 조회"""
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 200)

    def test_post_forbiddenword_fail_if_not_logged_in(self):
        """금지어 생성시 로그인 확인"""
        response = self.client.post(
            path=self.path,
            data=self.word_data,
        )
        self.assertEqual(response.status_code, 401)

    def test_post_exist_forbiddenword(self):
        """이미 존재하는 금지어 생성 실패"""
        response = self.client.post(
            path=self.path,
            data={"word": "word2"},
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 400)

    def test_post_forbiddenword_admin(self):
        """admin 금지어 생성 성공"""
        response = self.client.post(
            path=self.path,
            data=self.word_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 201)

    def test_post_forbiddenword_subadmin(self):
        """sub admin 금지어 생성 성공"""
        response = self.client.post(
            path=self.path,
            data=self.word_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token2}",
        )
        self.assertEqual(response.status_code, 201)


class CommunityBookmarkViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test1@naver.com",
            "name": "test1",
            "password": "test123!",
        }
        cls.user = User.objects.create_user("test1@naver.com", "test1", "test123!")
        cls.community = Community.objects.create(
            title="title1", introduction="introduction1"
        )
        cls.path = reverse(
            "community_bookmark_view", kwargs={"community_name": "title1"}
        )

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]

    def test_add_bookmark_fail_if_not_logged_in(self):
        """북마크 등록시 로그인 확인"""
        response = self.client.post(
            path=self.path,
        )
        self.assertEqual(response.status_code, 401)

    def test_add_bookmark(self):
        """북마크 등록 성공"""
        response = self.client.post(
            path=self.path, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)

    def test_remove_bookmark(self):
        """북마크 취소 성공"""
        self.community.bookmarked.add(self.user)

        response = self.client.post(
            path=self.path, HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )
        self.assertEqual(response.status_code, 200)
