from projectapp import views
from django.urls import path
from django.contrib.auth.views import LogoutView

urlpatterns = [ 
    path("", views.home, name="home" ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile", views.profile, name = "profile"),
    path("about", views.about, name="about" ),
    path("posts", views.posts, name="posts" ),
    path("posts/add/", views.add_post, name="add_post" ),
    path("post/<str:pk>/", views.post, name="post" ),
    path("post/<str:pk>/edit/", views.edit_post, name = "edit_post"),
    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_create, name="student_add"),
    path("students/<int:pk>/", views.student_detail, name="student_detail"),
    path("students/<int:pk>/edit/", views.student_update, name="student_edit"),
    path("students/<int:pk>/delete/", views.student_delete, name="student_delete"),
    path("user/form/", views.display_form, name = "user_form"),
    path("submit/form/", views.submit_form, name = "submit_form"),
    path("user/loki_user/", views.loki_user, name = "loki_user"),
    path("user/create/", views.create_user, name="create_user"),
]