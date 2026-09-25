from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from projectapp.models import GameCodeSubmission, Student


class GameDeveloperRegistrationTests(TestCase):
    def test_game_developer_model_can_be_created(self):
        developer = Student.objects.create(
            first_name="Ava",
            last_name="Storm",
            email="ava@pixelforge.dev",
            age=28,
            department="Gameplay Programming",
        )

        self.assertEqual(developer.first_name, "Ava")
        self.assertEqual(developer.last_name, "Storm")
        self.assertEqual(str(developer), "Ava Storm")

    def test_game_dev_list_page_loads(self):
        response = self.client.get(reverse("student_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Game Developers")

    def test_non_admin_cannot_register_developer(self):
        developer = User.objects.create_user(username="developer", password="test-password-123")
        self.client.force_login(developer)

        response = self.client.get(reverse("student_add"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_admin_can_register_developer(self):
        admin = User.objects.create_user(
            username="admin",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(admin)

        response = self.client.post(reverse("student_add"), {
            "first_name": "Ava",
            "last_name": "Storm",
            "email": "ava@example.com",
            "age": 28,
            "department": "Gameplay Programming",
            "username": "ava-storm",
            "password": "Strong-Developer-Password-123!",
            "password_confirm": "Strong-Developer-Password-123!",
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Student.objects.count(), 1)
        self.assertTrue(User.objects.filter(username="ava-storm").exists())
        self.client.logout()
        self.assertTrue(self.client.login(username="ava-storm", password="Strong-Developer-Password-123!"))

    def test_admin_login_returns_to_developer_registration(self):
        User.objects.create_user(
            username="admin",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        response = self.client.post(
            reverse("login"),
            {"username": "admin", "password": "test-password-123", "next": reverse("student_add")},
        )

        self.assertRedirects(response, reverse("student_add"))

    def test_account_creation_redirects_to_login(self):
        response = self.client.get(reverse("create_user"))

        self.assertRedirects(response, reverse("login"))
        self.assertEqual(User.objects.count(), 0)

    def test_legacy_account_creation_redirects_to_login(self):
        response = self.client.post(reverse("loki_user"), {
            "username": "blocked-user",
            "email": "blocked@example.com",
            "password": "test-password-123",
            "confirm_password": "test-password-123",
        })

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(User.objects.filter(username="blocked-user").exists())

    def test_non_admin_can_submit_game_code(self):
        developer = User.objects.create_user(username="developer", password="test-password-123")
        self.client.force_login(developer)

        response = self.client.post(reverse("game_code"), {
            "title": "Player Dash",
            "language": "Python",
            "description": "Adds a dash movement mechanic.",
            "code": "def dash(player):\n    player.speed *= 2",
        })

        self.assertRedirects(response, reverse("game_code"))
        submission = GameCodeSubmission.objects.get()
        self.assertEqual(submission.developer, developer)
        self.assertEqual(submission.title, "Player Dash")

    def test_admin_cannot_open_game_code_workspace(self):
        admin = User.objects.create_user(username="admin", password="test-password-123", is_staff=True)
        self.client.force_login(admin)

        response = self.client.get(reverse("game_code"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])
