from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='headed_departments')
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Program(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., B.Tech, M.Tech
    code = models.CharField(max_length=10, unique=True)  # e.g., BT, MT

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Batch(models.Model):
    year = models.CharField(max_length=9)  # e.g., "2024-2026"
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, default=1, on_delete=models.CASCADE)

    # Example for Batch
    class Meta:
        unique_together = ('year', 'department', 'program')

    def __str__(self):
        return f"{self.program.code} - {self.department.code} - Batch {self.year}"
    
class AcademicYear(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='academic_years')
    start_year = models.IntegerField()  # e.g., 2024
    end_year = models.IntegerField()    # e.g., 2025

    class Meta:
        unique_together = ('batch', 'start_year', 'end_year')

    def __str__(self):
        return f"{self.start_year}-{self.end_year} ({self.batch.year})"

class Semester(models.Model):
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='semesters')
    number = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    name = models.CharField(max_length=50, blank=True)  # Optional: "Sem 1"

    def __str__(self):
        return f"{self.academic_year} - Sem {self.number}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.batch}"

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)    
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class TeacherCourse(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['teacher', 'course', 'academic_year']


class StudentCourse(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    enrolled_date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ['student', 'course', 'academic_year']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.code}"

class AttendanceSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    topic = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ['course', 'date', 'start_time', 'academic_year']
    
    def __str__(self):
        return f"{self.course.code} - {self.date} ({self.start_time})"

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]
    
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendances')
    
    class Meta:
        unique_together = ['session', 'student']
    
    def __str__(self):
        return f"{self.student.username} - {self.session} - {self.status}"