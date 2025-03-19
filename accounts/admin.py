from django.contrib import admin
from .models import User,  Student, Advisor, Project, Submission, Schedule
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'major')
    search_fields = ('student_id', 'user__email')

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'advisor', 'status', 'category')
    filter_horizontal = ('students',)

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Advisor)
admin.site.register(Project)
admin.site.register(Submission)
admin.site.register(Schedule)

# ไม่ต้องลงทะเบียน Evaluation
# admin.site.register(Evaluation)