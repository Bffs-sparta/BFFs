from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Verify
from django.urls import reverse
from datetime import timedelta
from django.utils import timezone


# Create your tests here.


# class UserProfileViewTest(APITestCase):
#     # profile read
#     def test_profile_detail(self):
#         profile = self.user.id
#         url = reverse("profile:profile_view", kwargs={"user_id:user_id"})

#         response = self.client.get(url)
#         print(response.data)
#         self.assertEqual(response.status_code, 200)

#     # profile update
#     def test_profile_update(self):
#         profile = self.user.id
#         url = reverse("profile:profile_view", kwargs={"user_id": user_id})
#         update_data = {
#             "nickname": "unity",
#             "introduction": "import unittest",
#         }

#         response = self.client.force_authenticate(user=self.profile)
#         response = self.client.patch(url, update_data)
#         print(response.data)
#         self.assertEqual(response.status_code, 200)

#     # 회원탈퇴
#     def test_user_delete(self):
#         user = self.user.id
#         url = reverse("user:profile_view", kwargs={"user_id": user_id})
#         delete_data = {"password": "Universe48"}

#         response = self.client.delete(url, data=delete_data)
#         print(response.data)
#         self.assertEqual(response.status_code, 200)


# class GuestBookTest(APITestCase):
#     @classmethod
#     def test_comment_create_test(cls):
#         cls.email = "unity@ty.ty"
#         cls.name = "vuenity"
#         cls.password = "Universe48"
#         cls.user_data = {
#             "email": "unity@ty.ty",
#             "password": "universe48",
#             "name": "vuenity",
#         }
#         cls.profile_data = {
#             "nickname": "unity",
#             "introduction": "import unittest",
#             "region": "seoul",
#         }
#         cls.user = User.objects.create_user(
#             name=cls.name,
#         )


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

    def test_sendMail(self):
        email = {"email": "test@test.com"}
        response = self.client.post(self.path, email)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

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
        self.assertEqual(response.data["msg"], "메일인증이 완료되었습니다")

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
        }

    def test_signup(self):
        response = self.client.post(self.path, self.test_user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["msg"], "회원가입이 완료되었습니다.")

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
        test_user = {"email": "test3@test.com", "password": "test1234@", "name": "test"}
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
        test_user = {"email": "test@test.com", "password": "test1234@"}
        self.user.login_count = 6
        self.user.save()
        response = self.client.post(self.path, test_user)
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
