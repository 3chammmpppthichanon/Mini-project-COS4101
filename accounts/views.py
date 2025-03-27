import os

from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, Http404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from .forms import SubmissionForm
from .models import User, Project, Advisor, Student, Submission, Schedule
from django.shortcuts import get_object_or_404


# Create your views here.
def index(request):
    """
    หน้าแรกของเว็บไซต์

    แสดงหน้าหลักพร้อมข้อมูลภาพรวมสำหรับผู้ใช้
    """
    projects = Project.objects.all()
    advisors = Advisor.objects.all()

    context = {
        'advisors': advisors,
        'projects': projects,
    }
    return render(request, "index.html", context)

def login(request):
    """
    การเข้าสู่ระบบของผู้ใช้

    จัดการการยืนยันตัวตนและลงชื่อเข้าใช้ระบบ
    """
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            messages.warning(request, "Invalid email or password.")
            return redirect("login")

    return render(request, "login.html")


@login_required
def logout(request):
    """
    การออกจากระบบ

    ทำการออกจากระบบและเคลียร์เซสชัน
    """

    auth.logout(request)
    return redirect("login")


# -----------------------------------------------------------------------------------------------------
# Advisor
def advisor_list(request):
    """
    แสดงรายชื่ออาจารย์ที่ปรึกษาทั้งหมด
    """

    advisors = Advisor.objects.all()
    return render(request, "teacher.html", {'advisors': advisors})

# -----------------------------------------------------------------------------------------------------
# CRUD for Project
def project_list(request):  # Display all project
    """
    แสดงรายการโครงงานทั้งหมด
    """

    projects = Project.objects.all()
    return render(request, 'project.html', {'projects': projects})

def completed_project(request):
    """
    แสดงรายการโครงงานที่เสร็จสิ้นแล้ว
    """

    projects = Project.objects.filter(status='Completed')
    return render(request, 'project.html', {'projects': projects})


@login_required
def add_project(request):
    """
    สร้างโครงงานใหม่

    สำหรับอาจารย์ที่ปรึกษาในการสร้างโครงงานใหม่
    """

    if request.method == 'POST':
        if request.user.role not in ['Advisor', 'Admin']:
            messages.error(request, "ไม่มีสิทธิ์สร้างโปรเจ็กต์")
            return redirect('project_list')

        if request.user.role == 'Advisor' and not hasattr(request.user, 'advisor_profile'):
            messages.error(request, "โปรไฟล์ Advisor ไม่สมบูรณ์")
            return redirect('project_list')


        project = Project.objects.create(
            title=request.POST['title'],
            description=request.POST['description'],
            status=request.POST['status'],
            category=request.POST['category'],
            advisor=request.user.advisor_profile if request.user.role == 'Advisor' else None
        )
        messages.success(request, "สร้างโปรเจ็กต์สำเร็จ")
        return redirect('project_detail', project_id=project.id)

    return render(request, 'project.html')


def project_detail(request, project_id):
    """
    แสดงรายละเอียดของโครงงาน

    Args:
        project_id: รหัสโครงงาน
    """

    project = get_object_or_404(Project, id=project_id)
    students = project.students.all()
    submissions = project.submissions.all()

    context = {
        'project': project,
        'students': students,
        'submissions': submissions,
    }
    return render(request, 'projects/detail.html', context)


@login_required
def update_project(request, project_id):
    """
    แก้ไขข้อมูลโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการแก้ไข
    """

    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        status = request.POST["status"]
        category = request.POST["category"]

        if not title or not description:
            return render(request, "update_project.html")

        project.title = title
        project.description = description
        project.status = status
        project.category = category
        project.save()
        return redirect('update_project.html')


@login_required
def delete_project(request, project_id):
    """
    ลบโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการลบ
    """

    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('project_list')

    return render(request, 'projects/confirm_delete.html', {'project': project})


def search_project(request):
    """
    ค้นหาโครงงาน

    ค้นหาโครงงานตามคำค้นที่ผู้ใช้ระบุ
    """

    query = request.GET.get('q')
    projects = Project.objects.all()

    if query:
        projects = projects.filter(
            Q(title__icontains=query) |
            Q(category__icontains=query) |
            Q(status__icontains=query)
        )

    return render(request, 'project_list.html', {'projects': projects})


@login_required
def add_students_to_project(request, project_id):
    """
    เพิ่มนักศึกษาเข้าโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการเพิ่มนักศึกษา
    """

    project = get_object_or_404(Project, id=project_id)

    if not (request.user.role == 'Admin' or
            (request.user.role == 'Advisor' and project.advisor == request.user.advisor_profile)):
        messages.error(request, "ไม่มีสิทธิ์ดำเนินการ")
        return redirect('project_list')

    if request.method == "POST":
        student_ids = request.POST.getlist("students")
        for student_id in student_ids:
            try:
                student = Student.objects.get(id=student_id)
                project.students.add(student)
            except Student.DoesNotExist:
                messages.warning(request, f"ไม่พบนักศึกษา ID {student_id}")

        messages.success(request, "เพิ่มนักศึกษาเรียบร้อย")
        return redirect("project_detail", project_id=project.id)

    # แสดงนักศึกษาที่ยังไม่เข้าร่วมโปรเจ็กต์
    students = Student.objects.exclude(projects=project)
    return render(request, 'projects/add_students.html', {'project': project, 'students': students})

# -----------------------------------------------------------------------------------------------------

#Submission Management
@login_required
def upload_submission(request, project_id):
    """
    อัปโหลดไฟล์งานสำหรับโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการอัปโหลดไฟล์
    """

    project = get_object_or_404(Project, id=project_id)

    # ตรวจสอบสิทธิ์นักศึกษา
    if request.user.role != 'Student' or not project.students.filter(user=request.user).exists():
        messages.error(request, "คุณไม่มีสิทธิ์อัพโหลดไฟล์")
        return redirect('project_detail', project_id=project_id)

    if request.method == "POST":
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.project = project
            submission.save()
            messages.success(request, "อัพโหลดไฟล์สำเร็จ")
            return redirect('project_detail', project_id=project_id)
    else:
        form = SubmissionForm()

    return render(request, 'submissions/upload.html', {
        'form': form,
        'project': project
    })

@login_required
def download_submission(request, submission_id):
    """
    ดาวน์โหลดไฟล์งานที่อัปโหลดไว้

    Args:
        submission_id: รหัสการส่งงานที่ต้องการดาวน์โหลด
    """

    submission = get_object_or_404(Submission, id = submission_id)

    if request.user.role == 'Advisor' and submission.project.advisor != request.user.advisor_profile:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ดาวน์โหลดไฟล์นี้")

    file_path = submission.file.path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
            return response
    raise Http404
# -----------------------------------------------------------------------------------------------------
@login_required
def create_schedule(request, project_id):
    """
    สร้างตารางนัดหมายสำหรับโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการสร้างตารางนัดหมาย
    """

    project = get_object_or_404(Project, id=project_id)
    if not (request.user.role == 'Advisor' and project.advisor == request.user.advisor_profile):
        messages.error(request, "ไม่มีสิทธิ์สร้างการนัดหมาย")
        return redirect('project_detail', project_id=project_id)

    if request.method == 'POST':
        meeting_date = request.POST.get('meeting_date')
        topic = request.POST.get('topic')

        Schedule.objects.create(
            project=project,
            meeting_date=meeting_date,
            topic=topic,
            status='Planned'
        )
        messages.success(request, "สร้างการนัดหมายสำเร็จ")
        return redirect('view_schedule', project_id=project_id)

    return render(request, 'schedules/create_schedule.html')

def view_schedule(request, project_id):
    """
    ดูตารางนัดหมายของโครงงาน

    Args:
        project_id: รหัสโครงงานที่ต้องการดูตารางนัดหมาย
    """

    project = get_object_or_404(Project, id=project_id)
    schedules = Schedule.objects.filter(project=project)
    return render(request, 'schedules/schedule_list.html', {'schedules': schedules})




def manage_project(request):
    return render(request, 'manage.html', {'manage_project': manage_project})


def time_sent(request):
    return render(request, 'timesent.html', {'time_sent': time_sent})

def create_project(request):
    return render(request, 'create_project.html', {'create_project': create_project})

def sing_up(request):
    return render(request, 'sing_up.html', {'sing_up': sing_up})

def edit_project(request):
    return render(request, 'edit_project.html', {'edit_project': edit_project})