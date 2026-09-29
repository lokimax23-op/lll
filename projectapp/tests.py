from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.management import call_command
from unittest.mock import patch

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

    def test_non_admin_cannot_edit_or_delete_developer(self):
        admin = User.objects.create_user(
            username="admin",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )
        student = Student.objects.create(
            first_name="Ava",
            last_name="Storm",
            email="ava@example.com",
            age=28,
            department="Gameplay Programming",
        )
        developer = User.objects.create_user(username="developer", password="test-password-123")
        self.client.force_login(developer)

        edit_response = self.client.get(reverse("student_edit", args=[student.pk]))
        delete_response = self.client.get(reverse("student_delete", args=[student.pk]))

        self.assertEqual(edit_response.status_code, 302)
        self.assertIn(reverse("login"), edit_response["Location"])
        self.assertEqual(delete_response.status_code, 302)
        self.assertIn(reverse("login"), delete_response["Location"])

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
        developer_profile = Student.objects.get(email="ava@example.com")
        self.assertEqual(developer_profile.department, "Not specified")
        self.assertNotContains(self.client.get(reverse("student_add")), "Specialty / genre / engine")
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

    def test_admin_login_without_next_opens_admin_dashboard(self):
        User.objects.create_user(
            username="admin-dashboard",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        response = self.client.post(reverse("login"), {
            "username": "admin-dashboard",
            "password": "test-password-123",
        })

        self.assertRedirects(response, reverse("admin:index"))
        dashboard = self.client.get(reverse("admin:index"))
        self.assertEqual(dashboard.status_code, 200)
        self.assertContains(dashboard, "Students")
        self.assertContains(dashboard, "Game code submissions")

    def test_admin_login_from_publish_link_opens_admin_dashboard(self):
        User.objects.create_user(
            username="admin-publish-link",
            password="test-password-123",
            is_staff=True,
            is_superuser=True,
        )

        response = self.client.post(
            f"{reverse('login')}?next={reverse('game_code')}",
            {
                "username": "admin-publish-link",
                "password": "test-password-123",
                "next": reverse("game_code"),
            },
        )

        self.assertRedirects(response, reverse("admin:index"))

    def test_default_admin_command_uses_environment_credentials(self):
        environment = {
            "DJANGO_SUPERUSER_USERNAME": "render-admin",
            "DJANGO_SUPERUSER_EMAIL": "admin@example.com",
            "DJANGO_SUPERUSER_PASSWORD": "Secure-Render-Password-123!",
        }
        with patch.dict("os.environ", environment):
            call_command("create_default_admin", verbosity=0)

        admin = User.objects.get(username="render-admin")
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password(environment["DJANGO_SUPERUSER_PASSWORD"]))

    def test_developer_publish_sign_in_returns_to_code_workspace(self):
        developer = User.objects.create_user(username="publisher", password="test-password-123")
        Student.objects.create(
            user=developer,
            first_name="Game",
            last_name="Developer",
            email="publisher@example.com",
            age=28,
            department="Not specified",
        )

        login_url = f"{reverse('login')}?next={reverse('game_code')}"
        response = self.client.post(login_url, {
            "username": "publisher",
            "password": "test-password-123",
            "next": reverse("game_code"),
        })

        self.assertRedirects(response, reverse("game_code"))

    def test_public_signup_is_disabled(self):
        response = self.client.post(reverse("create_user"), {
            "username": "newdev",
            "password1": "Strong-Developer-Password-123!",
            "password2": "Strong-Developer-Password-123!",
        })

        self.assertRedirects(response, reverse("login"))
        self.assertFalse(User.objects.filter(username="newdev").exists())

    def test_homepage_routes_guests_and_staff_to_their_own_workflows(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Sign in to publish")
        self.assertNotContains(response, "Create developer account")

        staff_user = User.objects.create_user(
            username="moderator",
            password="test-password-123",
            is_staff=True,
        )
        self.client.force_login(staff_user)
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Open admin")
        self.assertNotContains(response, "+ Publish code")

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
        Student.objects.create(
            user=developer,
            first_name="Game",
            last_name="Developer",
            email="developer@example.com",
            age=28,
            department="Gameplay Programming",
        )
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

    def test_non_admin_without_developer_profile_can_open_code_workspace(self):
        user = User.objects.create_user(username="unregistered", password="test-password-123")
        self.client.force_login(user)

        response = self.client.get(reverse("game_code"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Drop Your Game Code")

    def test_admin_cannot_open_game_code_workspace(self):
        admin = User.objects.create_user(username="admin", password="test-password-123", is_staff=True)
        self.client.force_login(admin)

        response = self.client.get(reverse("game_code"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])


class GameCodeSharingTests(TestCase):
    def setUp(self):
        self.developer = User.objects.create_user(username="pixeldev", password="test-password-123")
        self.submission = GameCodeSubmission.objects.create(
            developer=self.developer,
            title="Wall jump controller",
            language="Python",
            description="A reusable platformer movement mechanic.",
            code="def wall_jump(player):\n    player.velocity_y = -12",
        )

    def test_public_feed_shows_submissions_to_anonymous_visitors(self):
        response = self.client.get(reverse("code_feed"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wall jump controller")
        self.assertContains(response, "@pixeldev")

    def test_public_feed_searches_titles_languages_and_developers(self):
        response = self.client.get(reverse("code_feed"), {"q": "Python"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wall jump controller")

        response = self.client.get(reverse("code_feed"), {"q": "missing"})
        self.assertNotContains(response, "Wall jump controller")

    def test_public_detail_shows_full_code_and_share_link(self):
        response = self.client.get(reverse("game_code_detail", args=[self.submission.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "def wall_jump(player):")
        self.assertContains(response, "pixeldev")
        self.assertContains(response, reverse("game_code_detail", args=[self.submission.pk]))

    def test_missing_public_detail_returns_404(self):
        response = self.client.get(reverse("game_code_detail", args=[99999]))

        self.assertEqual(response.status_code, 404)
