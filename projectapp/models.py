from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="developer_profile")
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField()
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Create your models here.
class Post(models.Model):
    name = models.CharField(max_length=50)
    body = models.TextField()
    is_published = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)
    last_edited = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Title: {self.name}, Last edited: {self.last_edited.date()}"


class GameCodeSubmission(models.Model):
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="game_code_submissions")
    title = models.CharField(max_length=120)
    language = models.CharField(max_length=40, default="Python")
    description = models.TextField(blank=True)
    code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} by {self.developer.username}"