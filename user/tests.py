from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase


from .models import User, Profile, GuestBook, Verify


class UserProfileViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "unity@ty.ty",
            "password": "universe48",
            "name": "vuenity",
        }
        cls.profile_data = {
            "nickname": "unity",
            "introduction": "import unittest",
            "region": "seoul",
        }
        cls.user = User.objects.create_user(**cls.user_data)

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]

    # profile read
    def test_profile_detail(self):
        url = reverse("profile_view")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        


    # profile update
    def test_profile_update(self):
        user_id = self.user.id
        url = reverse("profile_detail_view", kwargs={"user_id": user_id})
        update_data = {
            "nickname": "unity",
            "introduction": "import unittest",
        }

        response = self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, 200)
        
    # profile update(no permisiions)
    def test_profile_certified_update(self):
        user_id = self.user.id
        url = reverse("profile_detail_view", kwargs={"user_id": user_id})
        update_data = {
            "nickname": "unity",
            "introduction": "import unittest",
        }

        # response = self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, update_data)
        self.assertEqual(response.status_code, 401)
    
    # 회원탈퇴
    def test_user_delete(self):
        user_id = self.user.id
        url = reverse("profile_detail_view", kwargs={"user_id": user_id})
        delete_data = {"password": "universe48"}

        response = self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data=delete_data)
        self.assertEqual(response.status_code, 204)

    # 비밀번호가 다를 때 회원탈퇴 실패
    def test_user_delete_fail(self):
        user_id = self.user.id
        url = reverse("profile_detail_view", kwargs={"user_id": user_id})
        delete_data = {"password": "Universe48"}

        response = self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, data=delete_data)
        self.assertEqual(response.status_code, 400)


class GuestBookTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "unity@ty.ty",
            "password": "universe48",
            "name": "vuenity",
        }
        cls.profile_data = {
            "nickname": "unity",
            "introduction": "import unittest",
            "region": "seoul",
        }
        cls.comment_data = {
            "comment": "Wal, wal",
        }
        cls.comment_update_data = {
            "comment": "Wal, wal~",
        }
        cls.comment4_data = {
            "comment": "Wal, wal",
        }
        cls.user = User.objects.create_user(**cls.user_data)

        GuestBook.objects.create(
            user=cls.user, comment=cls.comment_data, profile_id=cls.user.id
        )

    def setUp(self):
        self.access_token = self.client.post(reverse("login"), self.user_data).data[
            "access"
        ]

    # guestbook comment read
    def test_get_comment_view(self):
        response = self.client.get(
            path=reverse("guestbook_view", kwargs={"profile_id": 1})
        )
        self.assertEqual(response.status_code, 200)


    # guestbook comment create
    def test_create_comment_view(self):
        response = self.client.post(
            path=reverse("guestbook_view", kwargs={"profile_id": 1}),
            data=self.comment_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    
        
    # guestbook comment update
    def test_comment_update_view(self):
        response = self.client.patch(
            path=reverse(
                "guestbook_detail_view", kwargs={"profile_id": 1, "guestbook_id": 1}
            ),
            data=self.comment_update_data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)
        
    # guestbook comment delete
    def test_comment_delete_view(self):
        response = self.client.delete(
            path=reverse(
                "guestbook_detail_view", kwargs={"profile_id": 1, "guestbook_id": 1}
            ),
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 204)
        

    # guestbook comment delete(no permisiions)
    def test_comment_certified_delete_view(self):
        response = self.client.delete(
            path=reverse(
                "guestbook_detail_view", kwargs={"profile_id": 1, "guestbook_id": 1}
            ),
        )
        self.assertEqual(response.status_code, 401)


class sendMailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test2@test.com",
            "password": "test1234@",
            "name": "test2",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.path = reverse("email")

    # def test_sendMail(self):
    #     email = {"email": "test@test.com"}
    #     response = self.client.post(self.path, email)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sendMail_none(self):
        email = {
            "email": "",
        }
        response = self.client.post(self.path, email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일을 작성해 주세요")

    def test_sendMail_regexError(self):
        email = {"email": "testtest.com"}
        response = self.client.post(self.path, email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일 형식이 올바르지 않습니다.")

    def test_sendMail_already(self):
        email = {"email": "test2@test.com"}
        response = self.client.post(self.path, email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이미 가입한 회원입니다.")


class verifyMailTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.verify_data = {"email": "test@test.com", "code": "123456"}
        cls.verify = Verify.objects.create(**cls.verify_data)
        cls.path = reverse("verify")

    def test_verifyMail(self):
        verify = self.verify_data
        response = self.client.post(self.path, verify)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "메일인증이 완료되었습니다")

    def test_verifyMail_none(self):
        verify = {"email": "", "code": ""}
        response = self.client.post(self.path, verify)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일이 입력이 안되어있습니다")

    def test_verifyMail_code(self):
        verify = {"email": "test@test.com", "code": "12345"}
        response = self.client.post(self.path, verify)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일이나 인증코드가 인증 코드가 틀렸습니다")

    def test_verifyMail_email(self):
        verify = {"email": "test2@test.com", "code": "123456"}
        response = self.client.post(self.path, verify)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "이메일이나 인증코드가 인증 코드가 틀렸습니다")


class signupTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test2@test.com",
            "password": "test1234@",
            "name": "test2",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.path = reverse("signup")
        cls.verify_data = {
            "email": "test@test.com",
            "code": "123456",
            "is_verify": True,
        }
        cls.verify = Verify.objects.create(**cls.verify_data)

    def setUp(self):
        self.test_user = {
            "email": "test@test.com",
            "password": "test1234@",
            "name": "test",
            "nickname": "test",
            "region": "test",
        }

    def test_signup(self):
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "회원가입이 완료되었습니다.")

    def test_signup_none(self):
        test_user = {"email": "", "password": "", "name": ""}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_email_regexError(self):
        test_user = {"email": "testtest.com", "password": "test1234@", "name": "test"}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_regexError(self):
        test_user = {"email": "test@test.com", "password": "test1234", "name": "test"}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_already(self):
        test_user = self.user_data
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_verify(self):
        test_user = {
            "email": "test3@test.com",
            "password": "test1234@",
            "name": "test",
            "nickname": "test",
            "region": "test",
        }
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class loginTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_data = {
            "email": "test@test.com",
            "password": "test1234@",
            "name": "test",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.path = reverse("login")

    def setUp(self):
        self.test_user = {"email": "test@test.com", "password": "test1234@"}

    def test_login(self):
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_none(self):
        test_user = {"email": "", "password": ""}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_email_notMatch(self):
        test_user = {"email": "testtest.com", "password": "test1234@"}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_password_notMatch(self):
        test_user = {"email": "test@test.com", "password": "test1234"}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_password_notMatch_5times(self):
        test_user = {"email": "test@test.com", "password": "test1234@@"}
        self.user.login_count = 6
        self.user.save()
        self.client.post(self.path, test_user)
        response = self.client.post(self.path, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_notExist(self):
        test_user = {"email": "test3@test.com", "password": "test1234@"}
        response = self.client.post(self.path, test_user)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_login_user_is_dormamt(self):
        self.user.is_dormant = True
        self.user.save()
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_is_withdraw(self):
        self.user.is_withdraw = True
        self.user.save()
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_finishBan(self):
        self.user.banned_at = timezone.now() - timedelta(days=1)
        self.user.save()
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
