from django.db import models


class Student(models.Model):
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