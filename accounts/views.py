import os

from django.conf import settings
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View

from .models import User, Project, Advisor, Student, Submission, Schedule
from django.shortcuts import get_object_or_404


# Create your views here.
def index(request):
    projects = Project.objects.all()
    advisors = Advisor.objects.all()

    context = {
        'advisors': advisors,
        'projects': projects,
    }
    return render(request, "index.html", context)

def login(request):
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
    auth.logout(request)
    return redirect("login")

# -----------------------------------------------------------------------------------------------------
# Advisor
def advisor_list(request):
    advisors = Advisor.objects.all()
    return render(request, "teacher.html", {'advisors': advisors})

# -----------------------------------------------------------------------------------------------------
# CRUD for Project
def project_list(request):  # Display all project
    projects = Project.objects.all()
    return render(request, 'project.html', {'projects': projects})

def completed_project(request):
    projects = Project.objects.filter(status='Completed')
    return render(request, 'project.html', {'projects': projects})

@login_required
def add_project(request):
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
    project = get_object_or_404(Project, id=project_id)
    students = project.students.all()

    context = {
        'project': project,
        'students': students,
    }

    return render(request, 'project.html', context)


@login_required
def update_project(request, project_id):
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
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project deleted successfully.")
        return redirect('project_list')

    return render(request, 'projects/confirm_delete.html', {'project': project})


def search_project(request):
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
class SubmissionView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        if not self._check_permission(request.user, project):
            return JsonResponse({'error': 'ไม่มีสิทธิ์อัพโหลด'}, status=403)

        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file found in the request.'}, status=400)

        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'submissions'))
        file_name = fs.save(uploaded_file.name, uploaded_file)

        submission = Submission.objects.create(
            project=project,
            file_name=fs.url(file_name),
            submitted_date=timezone.now(),
        )

        return JsonResponse({
            'message': 'File submitted successfully',
            'submission_id': submission.id,
            'file_url': submission.file_name,
        })

    def _check_permission(self, user, project):
        if user.role == 'Student':
            return user.student_profile in project.students.all()
        elif user.role == 'Advisor':
            return project.advisor == user.advisor_profile
        return False

    def get(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        submissions = Submission.objects.filter(project=project).values(
            'id', 'file_name', 'submitted_date', 'is_approved', 'feedback'
        )

        return JsonResponse({'submissions': list(submissions)}, safe=False)


def download_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id)
    file_path = os.path.join(settings.MEDIA_ROOT, submission.file_name)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
            return response
    return JsonResponse({'error': 'File not found.'}, status=404)


# -----------------------------------------------------------------------------------------------------
@login_required
def create_schedule(request, project_id):
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
    project = get_object_or_404(Project, id=project_id)
    schedules = Schedule.objects.filter(project=project)
    return render(request, 'schedules/schedule_list.html', {'schedules': schedules})