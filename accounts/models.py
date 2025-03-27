from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    ตัวจัดการผู้ใช้ที่กำหนดเอง

    ใช้สำหรับสร้างผู้ใช้และสร้างผู้ดูแลระบบโดยใช้อีเมลเป็นชื่อผู้ใช้หลัก
    """

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
    """
    โมเดลผู้ใช้ที่กำหนดเอง

    ใช้อีเมลเป็น username หลักและรองรับการกำหนดบทบาทต่างๆ
    """
    # ตัวเลือกสำหรับบทบาท
    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Advisor', 'Advisor'),
        ('Admin', 'Admin'),
    ]

    # ข้อมูลผู้ใช้
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # สถานะผู้ใช้
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # อ้างอิงที่จำเป็นสำหรับ PermissionsMixin
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

    # กำหนดตัวจัดการที่ใช้
    objects = CustomUserManager()

    # กำหนดฟิลด์หลักที่ใช้เป็นชื่อผู้ใช้
    USERNAME_FIELD = 'email'
    # ฟิลด์ที่จำเป็นต้องระบุเมื่อสร้างผู้ใช้
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email


# ------------------- Student -------------------
class Student(models.Model):
    """
    โมเดลข้อมูลนักศึกษา

    เก็บข้อมูลเพิ่มเติมของผู้ใช้ที่มีบทบาทเป็นนักศึกษา
    """
    # เชื่อมโยงกับผู้ใช้ (ลบเมื่อผู้ใช้ถูกลบ)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")

    # ข้อมูลนักศึกษา
    student_id = models.CharField(max_length=10, unique=True)
    year = models.IntegerField(null=True, blank=True)
    major = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.student_id})"


# ------------------- Advisor -------------------
class Advisor(models.Model):
    """
    โมเดลข้อมูลอาจารย์ที่ปรึกษา

    เก็บข้อมูลเพิ่มเติมของผู้ใช้ที่มีบทบาทเป็นอาจารย์ที่ปรึกษา
    """

    # ตัวเลือกคำนำหน้า
    TITLE_CHOICES = [
        ('ดร.', 'ดร.'),
        ('ผศ.', 'ผู้ช่วยศาสตราจารย์'),
        ('รศ.', 'รองศาสตราจารย์'),
        ('ศ.', 'ศาสตราจารย์'),
    ]

    # เชื่อมโยงกับผู้ใช้ (ลบเมื่อผู้ใช้ถูกลบ)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="advisor_profile")

    # ข้อมูลอาจารย์
    title = models.CharField(max_length=50, choices=TITLE_CHOICES)
    expertise = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} {self.user.first_name} {self.user.last_name}"


# ------------------- Project -------------------
class Project(models.Model):
    """
    โมเดลโครงงาน

    เก็บข้อมูลโครงงานนักศึกษา รวมถึงความสัมพันธ์กับนักศึกษาและอาจารย์ที่ปรึกษา
    """
    # ตัวเลือกสถานะโครงงาน
    STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]

    # ตัวเลือกประเภทโครงงาน
    CATEGORY_CHOICES = [
        ('Web Application', 'Web Application'),
        ('AI/ML', 'AI/ML'),
        ('Mobile App', 'Mobile App'),
        ('Other', 'Other')
    ]

    # เวลาที่สร้างและอัปเดต
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # รายละเอียดโครงงาน
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')

    # ความสัมพันธ์กับนักศึกษาและอาจารย์
    students = models.ManyToManyField(Student, related_name="enrolled_projects")
    advisor = models.ForeignKey(
        Advisor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects"
    )

    def __str__(self):
        """
        แสดงชื่อโครงงานและสถานะ
        """
        return f"{self.title} [{self.get_status_display()}]"


# ------------------- Submission -------------------
class Submission(models.Model):
    """
    โมเดลการส่งงาน

    เก็บข้อมูลไฟล์ที่นักศึกษาส่งสำหรับโครงงาน
    """
    # เชื่อมโยงกับโครงงาน (ลบเมื่อโครงงานถูกลบ)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="submissions")

    # ข้อมูลไฟล์
    file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    file_name = models.CharField(max_length=200)
    submitted_date = models.DateTimeField(auto_now_add=True)

    # สถานะการตรวจและข้อเสนอแนะ
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
    """
    โมเดลตารางนัดหมาย

    เก็บข้อมูลการนัดหมายระหว่างนักศึกษาและอาจารย์ที่ปรึกษา
    """
    # เชื่อมโยงกับโครงงาน (ลบเมื่อโครงงานถูกลบ)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="meetings")

    # ข้อมูลการนัดหมาย
    meeting_date = models.DateTimeField(default=timezone.now)
    topic = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[('Planned', 'Planned'), ('Completed', 'Completed')],
                              default='Planned')

    def __str__(self):
        """
        แสดงหัวข้อและวันที่นัดหมาย
        """
        return f"{self.topic} - {self.meeting_date.strftime('%d/%m/%Y %H:%M')}"
    


#Test Merge