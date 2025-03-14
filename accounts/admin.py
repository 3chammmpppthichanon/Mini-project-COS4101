from django.contrib import admin
from .models import User,  Student, Advisor, Project, Submission, Evaluation, Schedule
# Register your models here.

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Advisor)
admin.site.register(Project)
admin.site.register(Submission)
admin.site.register(Evaluation)
admin.site.register(Schedule)