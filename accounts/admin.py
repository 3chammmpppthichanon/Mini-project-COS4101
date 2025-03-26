from django.contrib import admin
from .models import User, Student, Advisor, Project, Submission, Schedule


# Register your models here.


# -----------------------------------------------------------------------------
# Admin Model Configurations
# -----------------------------------------------------------------------------


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff') # แสดงคอลัมน์เหล่านี้ในตาราง
    list_filter = ('role', 'is_active') # ตัวกรองด้านข้าง
    search_fields = ('email', 'first_name') # ช่องค้นหา


class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'major')
    search_fields = ('student_id', 'user__email')


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'advisor', 'status', 'category')
    filter_horizontal = ('students',)


# -----------------------------------------------------------------------------
# Model Registration
# -----------------------------------------------------------------------------

# ลงทะเบียนโมเดลกับหน้า Admin พร้อมการกำหนดค่า
admin.site.register(User)
admin.site.register(Student)
admin.site.register(Advisor)
admin.site.register(Project)
admin.site.register(Submission)
admin.site.register(Schedule)

# ไม่ต้องลงทะเบียน Evaluation
# admin.site.register(Evaluation)
