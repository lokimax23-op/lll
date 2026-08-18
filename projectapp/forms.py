from django import forms
from projectapp.models import Post, Student


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        # fields = ["name", "body"]


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "email",
            "age",
            "department",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Age"}),
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "Department"}),
        }
        