from django.test import TestCase
from django.urls import reverse

from projectapp.models import Student


class StudentCrudTests(TestCase):
    def test_student_model_can_be_created(self):
        student = Student.objects.create(
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
            age=36,
            department="Computer Science",
        )

        self.assertEqual(student.first_name, "Ada")
        self.assertEqual(student.last_name, "Lovelace")
        self.assertEqual(str(student), "Ada Lovelace")

    def test_student_list_page_loads(self):
        response = self.client.get(reverse("student_list"))
        self.assertEqual(response.status_code, 200)
