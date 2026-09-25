from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from projectapp.models import GameCodeSubmission, Post, Student


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"


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
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "Specialty / genre / engine"}),
        }


class DeveloperRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label="Developer username",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Login username"}),
    )
    password = forms.CharField(
        label="Login password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Temporary password"}),
    )
    password_confirm = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Repeat password"}),
    )

    class Meta:
        model = Student
        fields = ["first_name", "last_name", "email", "age", "department"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email address"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Age"}),
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "Specialty / genre / engine"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "The passwords do not match.")
        if password:
            try:
                password_validation.validate_password(password)
            except forms.ValidationError as error:
                self.add_error("password", error)
        return cleaned_data


class GameCodeSubmissionForm(forms.ModelForm):
    class Meta:
        model = GameCodeSubmission
        fields = ["title", "language", "description", "code"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Game system or feature name"}),
            "language": forms.TextInput(attrs={"class": "form-control", "placeholder": "Python, C#, JavaScript..."}),
            "description": forms.Textarea(attrs={"class": "form-control", "placeholder": "What does this code do?", "rows": 3}),
            "code": forms.Textarea(attrs={"class": "form-control code-editor", "placeholder": "Paste your game code here...", "rows": 18, "spellcheck": "false"}),
        }
        