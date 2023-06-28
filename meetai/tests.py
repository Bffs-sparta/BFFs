from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIClient

from user.models import User


class UserProfileViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()
        cls.user_data = {
            "email": "test@test.com",
            "password": "test12!@",
            "name": "testuser",
        }
        cls.profile_data = {
            "nickname": "testnick",
            "introduction": "introduction",
            "region": "seoul",
        }
        cls.user = User.objects.create_user(**cls.user_data)
        cls.access_token = cls.client.post(reverse("login"), cls.user_data).data[
            "access"
        ]
        cls.path = reverse("send_text_view")

    def setUp(self):
        self.user_input_data = {"user_input": "안녕!"}

    def test_get_ai_chat(self):
        response = self.client.get(
            path=self.path,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
        )
        self.assertEqual(response.status_code, 200)

    def test_get_ai_chat_not_login(self):
        response = self.client.get(
            path=self.path,
        )
        self.assertEqual(response.status_code, 401)

    # def test_post_ai_chat(self):
    #     response = self.client.post(
    #         path=self.path,
    #         data=self.user_input_data,
    #         HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
    #     )
    #     self.assertEqual(response.status_code, 200)
