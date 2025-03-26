from django.urls import path
from . import views

# กำหนดเส้นทาง URL ของแอปพลิเคชัน
urlpatterns = [
    # หน้าหลักและการจัดการผู้ใช้
    path('', views.index, name='index'),  # หน้าแรก
    path('login/', views.login, name='login'),  # หน้าเข้าสู่ระบบ
    path('logout/', views.logout, name='logout'),  # ออกจากระบบ

    # หน้าแสดงรายการต่างๆ
    path('project_list/', views.project_list, name='project_list'),  # รายการโครงงาน
    path('advisor_list/', views.advisor_list, name='advisor_list'),  # รายชื่ออาจารย์ที่ปรึกษา
    path('completed_projects/', views.completed_project, name='completed_projects'),  # โครงงานที่เสร็จสิ้นแล้ว

    # การจัดการโครงงาน
    path('Manage/', views.manage_project, name='manage_project'),  # จัดการโครงงาน
    path('Time_sent/', views.time_sent, name='time_sent'),  # เวลาส่งงาน

    # การส่งงานและดาวน์โหลด
    path('project/<int:project_id>/upload/', views.upload_submission, name='upload_submission'),  # อัปโหลดงาน
    path('download/<int:submission_id>/', views.download_submission, name='download_submission'),  # ดาวน์โหลดงาน
]
