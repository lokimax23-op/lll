from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from projectapp.models import Post, Student
from projectapp.forms import PostForm, StudentForm

# Create your views here.

def home(request):
    context = {'user': request.user}
    return render(request, "index.html", context)

def about(request):
    about_message = """
    This is a message for the about page from the backend. 
    """
    best_players = [ "Neymar", "Mbappe", "Messi", "Dembele"]
    GOAT = "Ronaldo"
    context = {"dml": about_message, "prog_name": "DmlStack", "age": 43, "best_players": best_players, "GOAT": GOAT,}
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
    return render(request, "student_list.html", context)


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    context = {"student": student}
    return render(request, "student_detail.html", context)


@login_required
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            messages.success(request, "Student added successfully!")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm()

    context = {"form": form, "title": "Add Student"}
    return render(request, "student_form.html", context)


@login_required
def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student updated successfully!")
            return redirect("student_detail", pk=student.pk)
    else:
        form = StudentForm(instance=student)

    context = {"form": form, "title": "Edit Student", "student": student}
    return render(request, "student_form.html", context)


@login_required
def student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        student.delete()
        messages.success(request, "Student deleted successfully!")
        return redirect("student_list")

    context = {"student": student}
    return render(request, "student_confirm_delete.html", context)


def loki_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if not (username and email and password and confirm_password):
            messages.error(request, "All fields are required!")
            return redirect("loki_user")
        
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("loki_user")
        
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already exists!")
            return redirect("loki_user")
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("loki_user")        
        
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long!")
            return redirect("loki_user")
        
        # Create the user
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "User registered successfully!")
        return redirect("loki_user")
    
    return render(request, "loki_user.html")


def create_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully! Please log in with your credentials.")
            return redirect("login")
    else:
        form = UserCreationForm()

    context = {"form": form}
    return render(request, "signup.html", context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password!")
    else:
        form = AuthenticationForm()
    
    context = {"form": form}
    return render(request, "login.html", context)


class CustomLogoutView(LogoutView):
    template_name = 'logout.html'
    
    def get_redirect_url(self):
        messages.success(self.request, "You have been logged out successfully!")
        return super().get_redirect_url()

