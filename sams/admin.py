from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'employee_id', 'student_id']
    list_filter = ['role', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'employee_id', 'student_id', 'phone')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'head']
    search_fields = ['name', 'code']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'semester', 'credits']
    list_filter = ['department', 'semester']
    search_fields = ['name', 'code']

@admin.register(TeacherCourse)
class TeacherCourseAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'course', 'academic_year']
    list_filter = ['academic_year', 'course__department']

@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'academic_year', 'enrolled_date']
    list_filter = ['academic_year', 'course__department']

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher', 'date', 'start_time', 'end_time']
    list_filter = ['date', 'course__department']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'marked_at', 'marked_by']
    list_filter = ['status', 'session__date', 'session__course']
    search_fields = ['student__username', 'session__course__name']