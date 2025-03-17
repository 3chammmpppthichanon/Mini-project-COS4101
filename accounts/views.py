from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import User, Project, Advisor, Student
from django.shortcuts import get_object_or_404


# Create your views here.

def index(request):
    return HttpResponse("You're at the index page.")


"""
def signup(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        conform_password = request.POST.get("conform_password")

        if User.objects.filter(email=email).exists():
            messages.warning(request, "Email already exists.")
            return redirect("signup")
        elif password != conform_password:
            messages.warning(request, "Password do not match.")
            return redirect("signup")

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect("login")
    else:
        return render(request, "register/signup.html")
"""


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

    return render(request, "register/login.html")


@login_required
def logout(request):
    auth.logout(request)
    return redirect("login")


# -----------------------------------------------------------------------------------------------------
# CRUD for Project
def project_list(request):  # Display all project
    projects = Project.objects.all()
    return render(request, 'something.html', {'projects': projects})


@login_required
def add_project(request):  # Create some project
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        status = request.POST["status"]
        category = request.POST["category"]

        if not title or not description:
            return render(request, 'projects/add_project.html', {
                'error': 'Title and Description are required!'
            })

        Project.objects.create(
            title=title,
            description=description,
            status=status,
            category=category,
        )
    return redirect('project_list')

    return render(request, 'projects/add_project.html')


def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    students = project.students.all()

    context = {
        'project': project,
        'students': students,
    }

    return render(request, 'projects/project_detail.html', context)


@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        status = request.POST["status"]
        category = request.POST["category"]

        if not title or not description:
            return render(request, "something.html")

        project.title = title
        project.description = description
        project.status = status
        project.category = category
        project.save()
        return redirect('something.html')


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
    project = get_object_or_404(Project, id=project_id)  # Get a project

    if request.method == "POST":
        student_ids = request.POST.getlist("students")
        for student_id in student_ids:
            try:
                student = User.objects.get(id=student_ids)
                project.students.add(student)
            except Student.DoesNotExist:
                messages.warning(request, f"Student with ID {student_id} does not exist.")

        messages.success(request, "Students added successfully.")
        return redirect("project_detail", project_id=project.id)

    students = Student.objects.exclude(project=project)

    return render(request, 'add_students.html', {'project': project, 'students': students})

# -----------------------------------------------------------------------------------------------------
