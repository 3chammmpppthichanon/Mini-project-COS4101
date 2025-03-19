from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, role, password=None):
        if role not in dict(User.ROLE_CHOICES).keys():
            raise ValueError(f"Invalid role. Must be one of: {User.ROLE_CHOICES}")

        if not email:
            raise ValueError("The email address is required")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password):
        user = self.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role="Admin",
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Advisor', 'Advisor'),
        ('Admin', 'Admin'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Add related_name to avoid conflict
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


# ------------------- Student -------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=15, unique=True)
    year = models.IntegerField()
    major = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.student_id})"


# ------------------- Advisor -------------------
class Advisor(models.Model):
    TITLE_CHOICES = [
        ('ดร.', 'ดร.'),
        ('ผศ.', 'ผู้ช่วยศาสตราจารย์'),
        ('รศ.', 'รองศาสตราจารย์'),
        ('ศ.', 'ศาสตราจารย์'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="advisor_profile")
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    expertise = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} {self.user.first_name} {self.user.last_name}"


# ------------------- Project -------------------
class Project(models.Model):
    STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]

    CATEGORY_CHOICES = [
        ('Web Application', 'Web Application'),
        ('AI/ML', 'AI/ML'),
        ('Mobile App', 'Mobile App'),
        ('Other', 'Other')
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    students = models.ManyToManyField(Student, related_name="enrolled_projects")
    advisor = models.ForeignKey(
        Advisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects"
    )

    def __str__(self):
        return self.title


# ------------------- Submission -------------------
class Submission(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    file_name = models.CharField(max_length=200)
    submitted_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Submission for {self.project.title} - {self.file_name}"

# # ------------------- Evaluation -------------------
# class Evaluation(models.Model):
#     project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="evaluations")
#     evaluator = models.ForeignKey(Advisor, on_delete=models.CASCADE, related_name="evaluations_given")
#     score = models.FloatField()
#     review = models.TextField()
#
#     def __str__(self):
#         return f"Evaluation for {self.project.title} by {self.evaluator}"


# ------------------- Schedule -------------------
class Schedule(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="meetings")
    meeting_date = models.DateTimeField(default=timezone.now)
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[('Planned', 'Planned'), ('Completed', 'Completed')],
                              default='Planned')

    def __str__(self):
        return f"Meeting for {self.project.title} on {self.meeting_date}"
