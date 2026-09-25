from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.contrib import messages
from django.views import View
from django.utils.http import url_has_allowed_host_and_scheme
from projectapp.models import GameCodeSubmission, Post, Student
from projectapp.forms import DeveloperRegistrationForm, GameCodeSubmissionForm, PostForm, StudentForm

# Create your views here.

def home(request):
    context = {'user': request.user, 'studio_name': 'GameCaptain'}
    return render(request, "index.html", context)

def about(request):
    studio_info = {
        "name": "GameCaptain Studio",
        "mission": "Build immersive worlds and unforgettable gameplay experiences.",
        "focus": ["Gameplay Programming", "Art Direction", "VFX", "Production", "QA"],
        "goal": "Recruit top developers for the next blockbuster release.",
    }
    context = {"studio": studio_info}
    return render(request, "about.html", context)

def profile(request):
    me = {
        "name": "Favour",
        "class": "Python",
        "age": 54
    }
    return JsonResponse(me)

@login_required
def posts(request):
    posts = Post.objects.all()
    context = {"posts": posts}
    return render(request, "posts.html", context)

def post(request, pk):
    # the_post = Post.objects.get(pk = pk)
    the_post = get_object_or_404(Post, pk = pk)
    context = {"post": the_post}
    return render(request, "post.html", context)

def display_form(request):
    return render(request, "user_form.html")

def submit_form(request):
    if request.method == "POST":
        name = request.POST.get("name")
        dept = request.POST.get("department")

        values = {"name": name, "department": dept}
        return JsonResponse(values)
    return redirect("user_form")

@login_required
def add_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Post created successfully!")
            return redirect("posts")
    else:
        form = PostForm()

    context = {"post_form": form, "title": "Add Post"}
    return render(request, "post_form.html", context)


@login_required
def edit_post(request, pk):
    the_post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=the_post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect("post", pk=the_post.pk)
    else:
        form = PostForm(instance=the_post)

    context = {"post_form": form, "post": the_post, "title": "Edit Post"}
    return render(request, "post_form.html", context)


def student_list(request):
    students = Student.objects.all().order_by("last_name", "first_name")
    context = {"students": students}
    return render(request, "developer_list.html", context)


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    context = {"student": student}
    return render(request, "developer_detail.html", context)


def admin_only(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@user_passes_test(admin_only, login_url="login")
def student_create(request):
    if request.method == "POST":
        form = DeveloperRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                developer_user = User.objects.create_user(
                    username=form.cleaned_data["username"],
                    email=form.cleaned_data["email"],
                    password=form.cleaned_data["password"],
                )
                student = form.save(commit=False)
                student.user = developer_user
                student.save()
            messages.success(request, "Developer added successfully!")
            return redirect("student_detail", pk=student.pk)
    else:
        form = DeveloperRegistrationForm()

    context = {"form": form, "title": "Add Developer"}
    return render(request, "developer_form.html", context)


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Developer updated successfully!")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)

    context = {"form": form, "title": "Edit Developer", "student": student}
    return render(request, "developer_form.html", context)


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Developer deleted successfully!")
        return redirect("student_list")

    context = {"student": student}
    return render(request, "developer_confirm_delete.html", context)


def developer_only(user):
    return user.is_authenticated and not user.is_staff


@user_passes_test(developer_only, login_url="login")
def game_code(request):
    if request.method == "POST":
        form = GameCodeSubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.developer = request.user
            submission.save()
            messages.success(request, "Game code submitted successfully!")
            return redirect("game_code")
    else:
        form = GameCodeSubmissionForm()

    submissions = GameCodeSubmission.objects.filter(developer=request.user)
    return render(request, "game_code.html", {"form": form, "submissions": submissions})


def loki_user(request):
    messages.info(request, "Account creation is disabled. Please log in.")
    return redirect("login")


def create_user(request):
    messages.info(request, "Account creation is disabled. Please log in.")
    return redirect("login")


def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next")
    if not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
        next_url = None

    if request.user.is_authenticated:
        return redirect(next_url or "home")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url or "home")
        else:
            messages.error(request, "Invalid username or password!")
    else:
        form = AuthenticationForm()
    
    context = {"form": form, "next_url": next_url}
    return render(request, "login.html", context)


class CustomLogoutView(LogoutView):
    template_name = 'logout.html'
    
    def get_redirect_url(self):
        messages.success(self.request, "You have been logged out successfully!")
        url = super().get_redirect_url()
        return url or '/'

