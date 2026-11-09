from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_returns_token_and_user(self):
        response = self.client.post(
            "/api/auth/register/",
            {"username": "ana", "email": "ana@example.com", "password": "una-clave-segura-1"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], "ana@example.com")

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user("ana", "ana@example.com", "una-clave-segura-1")
        response = self.client.post(
            "/api/auth/register/",
            {"username": "otra", "email": "ANA@example.com", "password": "una-clave-segura-1"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            "/api/auth/register/", {"username": "ana", "email": "ana@example.com", "password": "123"}
        )
        self.assertEqual(response.status_code, 400)

    def test_login_me_logout(self):
        User.objects.create_user("ana", "ana@example.com", "una-clave-segura-1")
        login = self.client.post("/api/auth/login/", {"username": "ana", "password": "una-clave-segura-1"})
        self.assertEqual(login.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['token']}")
        self.assertEqual(self.client.get("/api/auth/me/").data["username"], "ana")
        self.assertEqual(self.client.post("/api/auth/logout/").status_code, 204)
        self.assertEqual(self.client.get("/api/auth/me/").status_code, 401)
