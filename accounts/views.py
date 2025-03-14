from gc import get_objects

from django.contrib import messages, auth
from django.http import HttpResponse
from django.shortcuts import render, redirect
from unicodedata import category

from .models import User, Project, Advisor
# from .forms import ProjectForm
from django.shortcuts import get_object_or_404


# Create your views here.

def index(request):
    return HttpResponse("You're at the index page.")
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


def logout(request):
    auth.logout(request)
    return redirect("login")

#CRUD for Project
def project_list(request): #Display all project
    projects = Project.objects.all()
    return render(request, 'something.html', {'projects': projects})

def add_project(request): #Create some project
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
    return render(request, 'projects/project_detail.html', {'project': project})

def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method =="POST":
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

def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        project.delete()
        return redirect('something.html')

    return render(request, 'something.html')

#Views for user