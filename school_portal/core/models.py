from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils.text import  slugify
from django.utils import timezone
from django.utils.crypto import get_random_string
import random, uuid






class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Message from {self.name}({self.email})"


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True, null=True)
    body = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
       return self.title 

    


    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password=password, **extra_fields)


class CustomUser(AbstractUser, PermissionsMixin):
    ROLE_STUDENT = 'student'
    ROLE_TEACHER = 'teacher'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_TEACHER, 'Teacher'),
    ]

    username = None
    admission_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        if not name:
            name = self.email or f"User-{self.pk}"
        return f"{name} ({self.admission_number})"

    def save(self, *args, **kwargs):
        # Auto-generate admission number logic here if needed
        if not self.admission_number and self.role == 'teacher':
            while True:
                new_id = f"TEA-{uuid.uuid4().hex[:8].upper()}"
                if not CustomUser.objects.filter(admission_number=new_id).exists():
                    self.admission_number = new_id
                    break
        if not self.username:
            self.username = f"{slugify(self.first_name or 'user')}-{uuid.uuid4().hex[:4]}"
        super().save(*args, **kwargs)


# STUDENT PROFILE
class StudentProfile(models.Model):
    CLASS_CHOICES = [
        ('P1', 'Primary 1'),
        ('P2', 'Primary 2'),
        ('P3', 'Primary 3'),
        ('P4', 'Primary 4'),
        ('P5', 'Primary 5'),
        ('P6', 'Primary 6'),
        ('JSS1', 'JSS1'),
        ('JSS2', 'JSS2'),
        ('JSS3', 'JSS3'),
        ('SS1', 'SS1'),
        ('SS2', 'SS2'),
        ('SS3', 'SS3'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='studentprofile'
    )
    student_class = models.ForeignKey('StudentClass', on_delete=models.SET_NULL, null=True)
    admission_number = models.CharField(max_length=50, default='0000')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        if not self.user:
            return "Unnamed Student"
        return f"{self.user.first_name} {self.user.last_name} ({self.user.admission_number})"

# TEACHER PROFILE

class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )
    employee_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="Auto-generated if left blank"
    )
    subject = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Subject taught by the teacher"
    )
    profile_picture = models.ImageField(
        upload_to='teacher_profiles/',
        blank=True,
        null=True,
        help_text="Upload a profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not provided
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        super().save(*args, **kwargs)

    def generate_employee_id(self):
        # Generate a unique 8-character alphanumeric ID
        return f"EMP-{get_random_string(8).upper()}"

    def __str__(self):
        full_name = self.user.get_full_name()
        username = self.user.username
        subject = self.subject or "No Subject"
        
        if full_name:
            return f"{full_name} ({subject})"
        elif hasattr(self.user, 'email') and self.user.email:
            return f"{self.user.email} ({subject})"
        else:
            return f"Teacher {self.employee_id} ({subject})"

    class Meta:
        verbose_name = "Teacher Profile"
        verbose_name_plural = "Teacher Profiles"


# CLASSES
class StudentClass(models.Model):
    GRADE_CHOICES = [
        ('P1', 'Primary 1'),
        ('P2', 'Primary 2'),
        ('P3', 'Primary 3'),
        ('P4', 'Primary 4'),
        ('P5', 'Primary 5'),
        ('P6', 'Primary 6'),
        ('JSS1', 'Secondary 1'),
        ('JSS2', 'Secondary 2'),
        ('JSS3', 'Secondary 3'),
        ('SS1', 'Secondary 1'),
        ('SS2', 'Secondary 2'),
        ('SS3', 'Secondary 3')
    ]
    
    name = models.CharField(max_length=50)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    class_teacher = models.ForeignKey('TeacherProfile', on_delete=models.SET_NULL, null=True)
   

    def __str__(self):
        return f"{self.name} ({self.get_grade_display()})"


# SUBJECTS
class Subject(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=10)
    is_core = models.BooleanField(default=True)  

    def __str__(self):
        return f"{self.code} - {self.name}"


class ClassSubject(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE,null=True, blank=True  )
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('student_class', 'subject')

    def __str__(self):
        return f"{self.student_class} - {self.subject}"


# ASSIGNMENTS
class Assignment(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    due_date = models.DateField()
    assigned_class = models.ForeignKey('StudentClass', on_delete=models.CASCADE,  null=True, blank=True )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        limit_choices_to={'role': 'teacher'}
    )

    def __str__(self):
        return f"{self.title} ({self.assigned_class.name})"


# SUBMISSIONS
class Submission(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    file = models.FileField(upload_to='submissions/')
    submitted_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submitted by {self.student.email}"


# DASHBOARD / OTHER MODELS
class StudentDashboardProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    hobbies = models.TextField(blank=True, help_text="Separate hobbies with commas")
    current_class = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


# NOTES
class Note(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'}
    )
    subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    target_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='notes/')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Class Note"
        verbose_name_plural = "Class Notes"

    def __str__(self):
        return f"{self.title} ({self.target_class.name})"
    

    #pay fees 
    

class Payment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)  # Paystack transaction ref
    status = models.CharField(max_length=50, default='pending')
    paid_at = models.DateTimeField(auto_now_add=True)
    receipt_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.amount}"
    



class ClassFee(models.Model):
    student_class = models.ForeignKey('StudentClass', on_delete=models.CASCADE)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student_class} - ₦{self.total_fee}"

class StudentFee(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    class_fee = models.ForeignKey(ClassFee,on_delete=models.CASCADE,  null=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('partial', 'Partially Paid'),
            ('paid', 'Fully Paid')
        ],
        default='pending'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def balance(self):
        return self.class_fee.total_fee - self.paid_amount if self.class_fee else 0

    def update_status(self):
        if self.class_fee and self.paid_amount >= self.class_fee.total_fee:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'pending'
        self.save()    

#leave


class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ]

    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    purpose = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.status}"
    




#grading


class SubjectGrade(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    subject = models.CharField(max_length=100)
    first_ca = models.DecimalField(max_digits=5, decimal_places=2)
    second_ca = models.DecimalField(max_digits=5, decimal_places=2)
    third_ca = models.DecimalField(max_digits=5, decimal_places=2)
    exam = models.DecimalField(max_digits=5, decimal_places=2)
    total_score = models.DecimalField(max_digits=6, decimal_places=2, blank=True)

    term = models.CharField(max_length=20)
    session = models.CharField(max_length=20)
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='grades_uploaded'
    )
    is_approved = models.BooleanField(default=False) 
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_score = self.first_ca + self.second_ca + self.third_ca + self.exam
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject} - {self.total_score}"


class TermResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'student'}
    )
    TERM_CHOICES = [
    ('First Term', 'First Term'),
    ('Second Term', 'Second Term'),
    ('Third Term', 'Third Term'),
    ]
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    session = models.CharField(max_length=20)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.term} - {self.session} - {'Published' if self.is_published else 'Unpublished'}"
    




#apply now page 

# core/models.py



class AdmissionApplication(models.Model):
    CLASS_CHOICES = [
        ('JSS1', 'JSS1'),
        ('JSS2', 'JSS2'),
        ('JSS3', 'JSS3'),
        ('SS1', 'SS1'),
        ('SS2', 'SS2'),
        ('SS3', 'SS3'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    previous_school = models.CharField(max_length=200, blank=True)
    date_of_birth = models.DateField()
    class_applying_to = models.CharField(max_length=10, choices=CLASS_CHOICES)  # ← add this
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('declined', 'Declined')],
        default='pending'
    )
    admission_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.status}"
