from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse

from .models import User

# Create your tests here.


class UserProfileViewTest(APITestCase):
    # profile read
    def test_profile_detail(self):
        profile = self.user.id
        url = reverse("profile:profile_view", kwargs={"user_id:user_id"})

        response = self.client.get(url)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # profile update
    def test_profile_update(self):
        profile = self.user.id
        url = reverse("profile:profile_view", kwargs={"user_id": user_id})
        update_data = {
            "nickname": "unity",
            "introduction": "import unittest",
        }

        response = self.client.force_authenticate(user=self.profile)
        response = self.client.patch(url, update_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    # 회원탈퇴
    def test_user_delete(self):
        user = self.user.id
        url = reverse("user:profile_view", kwargs={"user_id": user_id})
        delete_data = {"password": "Universe48"}

        response = self.client.delete(url, data=delete_data)
        print(response.data)
        self.assertEqual(response.status_code, 200)


class GuestBookTest(APITestCase):
    @classmethod
    def test_comment_create_test(cls):
        cls.email = "unity@ty.ty"
        cls.name = "vuenity"
        cls.password = "Universe48"
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
        cls.user = User.objects.create_user(
            name=cls.name,
        )
