from django.contrib import admin
from projectapp.models import GameCodeSubmission, Post, Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
	list_display = ("first_name", "last_name", "email", "department", "user")
	search_fields = ("first_name", "last_name", "email", "user__username")
	list_filter = ("department",)


@admin.register(GameCodeSubmission)
class GameCodeSubmissionAdmin(admin.ModelAdmin):
	list_display = ("title", "language", "developer", "created_at")
	search_fields = ("title", "language", "developer__username")
	list_filter = ("language", "created_at")
	readonly_fields = ("created_at",)


admin.site.register(Post)