from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='attendance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Admin: User Management
    path('administrator/create-student/', views.create_student, name='create_student'),
    path('administrator/create-teacher/', views.create_teacher, name='create_teacher'),

    # administrator: Entity Creation
    path('administrator/create-department/', views.create_department, name='create_department'),
    path('administrator/create-course/', views.create_course, name='create_course'),
    path('administrator/create-batch/', views.create_batch, name='create_batch'),
    path('administrator/create-program/', views.create_program, name='create_program'),
    path('administrator/create-academic-year/', views.create_academic_year, name='create_academic_year'),
    path('administrator/create-semester/', views.create_semester, name='create_semester'),

    # administrator: Assignments & Reports
    path('administrator/assign-teacher/', views.assign_teacher_course, name='assign_teacher_course'),
    path('administrator/enroll-student/', views.enroll_student_course, name='enroll_student_course'),
    path('administrator/reports/', views.admin_reports, name='admin_reports'),

    path('administrator/bulk-enroll/', views.bulk_enroll_students, name='bulk_enroll_students'),
    
    # AJAX endpoints
    path('ajax/get-students-by-batch/', views.get_students_by_batch, name='ajax_get_students_by_batch'),
    path('ajax/get-courses-by-semester/', views.get_courses_by_semester, name='ajax_get_courses_by_semester'),
    path('ajax/get-student-courses/', views.get_student_courses, name='ajax_get_student_courses'),
    path('ajax/get-teacher-courses/', views.get_teacher_courses, name='ajax_get_teacher_courses'),
    path('ajax/remove-student-course/', views.remove_student_course, name='ajax_remove_student_course'),
    path('ajax/remove-teacher-course/', views.remove_teacher_course, name='ajax_remove_teacher_course'),

    # Teacher
    path('teacher/courses/', views.teacher_courses, name='teacher_courses'),
    path('teacher/mark-attendance/<int:course_id>/', views.mark_attendance, name='mark_attendance'),
    path('teacher/attendance-history/<int:course_id>/', views.attendance_history, name='attendance_history'),
    path('ajax/session-attendance/<int:session_id>/', views.session_attendance_detail, name='session_attendance_detail'),

    # Student
    path('student/attendance/', views.student_attendance, name='student_attendance'),

    path('administrator/programs/', views.program_list, name='program_list'),
    path('administrator/batches/', views.batch_list, name='batch_list'),
    path('administrator/academic_years/', views.academic_year_list, name='academic_year_list'),
    path('administrator/semesters/', views.semester_list, name='semester_list'),
    path('administrator/courses/', views.course_list, name='course_list'),
    path('administrator/students/', views.student_list, name='student_list'),
    path('administrator/teachers/', views.teacher_list, name='teacher_list'),
    path('administrator/departments/', views.department_list, name='department_list'),
    path('administrator/teacher-assignments/', views.teacher_course_assignments, name='teacher_course_assignments'),
    path('administrator/student-enrollments/', views.student_course_enrollments, name='student_course_enrollments'),

]
