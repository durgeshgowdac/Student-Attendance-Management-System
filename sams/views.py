from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *

def role_required(allowed_roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                messages.error(request, "You don't have permission to access this page.")
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def dashboard(request):
    context = {'user': request.user}
    
    if request.user.role == 'admin':
        # Basic counts
        total_students = User.objects.filter(role='student').count()
        total_teachers = User.objects.filter(role='teacher').count()
        total_courses = Course.objects.count()
        total_departments = Department.objects.count()
        total_batches = Batch.objects.count()
        total_programs = Program.objects.count()
        total_academic_years = AcademicYear.objects.count()
        total_semesters = Semester.objects.count()
        
        # Analytics data
        total_enrollments = StudentCourse.objects.count()
        total_assignments = TeacherCourse.objects.count()
        total_sessions = AttendanceSession.objects.count()
        
        # Calculate average attendance
        total_attendance_records = Attendance.objects.count()
        present_records = Attendance.objects.filter(status__in=['present', 'late']).count()
        avg_attendance = round((present_records / total_attendance_records * 100), 1) if total_attendance_records > 0 else 0
        
        context.update({
            'total_students': total_students,
            'total_teachers': total_teachers,
            'total_courses': total_courses,
            'total_departments': total_departments,
            'total_batches': total_batches,
            'total_programs': total_programs,
            'total_academic_years': total_academic_years,
            'total_semesters': total_semesters,
            'total_enrollments': total_enrollments,
            'total_assignments': total_assignments,
            'total_sessions': total_sessions,
            'avg_attendance': avg_attendance,
        })
        return render(request, 'attendance/admin_dashboard.html', context)
    
    elif request.user.role == 'teacher':
        teacher_courses = TeacherCourse.objects.filter(teacher=request.user)
        context.update({
            'courses': teacher_courses,
            'total_courses': teacher_courses.count(),
        })
        return render(request, 'attendance/teacher_dashboard.html', context)
    
    elif request.user.role == 'student':
        student_courses = StudentCourse.objects.filter(student=request.user).select_related('course__semester')
        
        # Group courses by semester
        semester_courses = {}
        
        for sc in student_courses:
            semester = sc.course.semester
            if semester not in semester_courses:
                semester_courses[semester] = []
            
            total_sessions = AttendanceSession.objects.filter(
                course=sc.course, 
                academic_year=sc.academic_year
            ).count()
            
            attended_sessions = Attendance.objects.filter(
                session__course=sc.course,
                student=request.user,
                status__in=['present', 'late']
            ).count()
            
            percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            semester_courses[semester].append({
                'course': sc.course,
                'total_sessions': total_sessions,
                'attended_sessions': attended_sessions,
                'percentage': round(percentage, 2)
            })
        
        context.update({
            'courses': student_courses,
            'semester_courses': semester_courses,
        })
        return render(request, 'attendance/student_dashboard.html', context)
    
    # 🔴 Missing role or invalid role fallback
    else:
        messages.error(request, "Invalid user role.")
        return redirect('login')

@login_required
@role_required(['teacher'])
def teacher_courses(request):
    courses = TeacherCourse.objects.filter(teacher=request.user)
    return render(request, 'attendance/teacher_courses.html', {'courses': courses})

@login_required
@role_required(['teacher'])
def mark_attendance(request, course_id):
    teacher_course = get_object_or_404(TeacherCourse, id=course_id, teacher=request.user)
    
    if request.method == 'POST':
        # Create new attendance session
        session = AttendanceSession.objects.create(
            course=teacher_course.course,
            teacher=request.user,
            date=request.POST.get('date'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            academic_year=teacher_course.academic_year,
            topic=request.POST.get('topic', '')
        )
        
        # Get all students enrolled in this course
        students = User.objects.filter(
            studentcourse__course=teacher_course.course,
            studentcourse__academic_year=teacher_course.academic_year
        )
        
        # Mark attendance for each student
        for student in students:
            status = request.POST.get(f'attendance_{student.id}', 'absent')
            Attendance.objects.create(
                session=session,
                student=student,
                status=status,
                marked_by=request.user
            )
        
        messages.success(request, 'Attendance marked successfully!')
        return redirect('teacher_courses')
    
    # Get students enrolled in this course
    students = User.objects.filter(
        studentcourse__course=teacher_course.course,
        studentcourse__academic_year=teacher_course.academic_year
    ).order_by('username')
    
    context = {
        'teacher_course': teacher_course,
        'students': students,
    }
    return render(request, 'attendance/mark_attendance.html', context)

@login_required
@role_required(['teacher'])
def attendance_history(request, course_id):
    teacher_course = get_object_or_404(TeacherCourse, id=course_id, teacher=request.user)
    
    sessions = AttendanceSession.objects.filter(
        course=teacher_course.course,
        academic_year=teacher_course.academic_year
    ).order_by('-date', '-start_time')

    # Annotate attendance counts manually
    for session in sessions:
        session.present_count = Attendance.objects.filter(session=session, status='present').count()
        session.absent_count = Attendance.objects.filter(session=session, status='absent').count()
        session.late_count = Attendance.objects.filter(session=session, status='late').count()

    context = {
        'teacher_course': teacher_course,
        'sessions': sessions,
    }
    return render(request, 'attendance/attendance_history.html', context)

from django.template.loader import render_to_string
from django.http import HttpResponse, Http404

@login_required
@role_required(['teacher'])
def session_attendance_detail(request, session_id):
    try:
        session = AttendanceSession.objects.get(pk=session_id, teacher=request.user)
    except AttendanceSession.DoesNotExist:
        raise Http404("Session not found")

    attendance_records = Attendance.objects.filter(session=session).select_related('student')

    html = render_to_string('attendance/partials/session_attendance_detail.html', {
        'session': session,
        'records': attendance_records
    })

    return HttpResponse(html)


@login_required
@role_required(['student'])
def student_attendance(request):
    student_courses = StudentCourse.objects.filter(student=request.user)
    attendance_data = []
    
    for sc in student_courses:
        attendances = Attendance.objects.filter(
            student=request.user,
            session__course=sc.course
        ).select_related('session')
        
        attendance_data.append({
            'course': sc.course,
            'attendances': attendances
        })
    
    return render(request, 'attendance/student_attendance.html', {'attendance_data': attendance_data})

@login_required
@role_required(['admin'])
def admin_reports(request):
    if request.method == 'GET' and 'course_id' in request.GET:
        course_id = request.GET.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        # Get attendance report for the course
        students = User.objects.filter(
            studentcourse__course=course,
            role='student'
        )
        
        report_data = []
        for student in students:
            total_sessions = AttendanceSession.objects.filter(course=course).count()
            attended_sessions = Attendance.objects.filter(
                student=student,
                session__course=course,
                status__in=['present', 'late']
            ).count()
            
            percentage = (attended_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            report_data.append({
                'student': student,
                'total_sessions': total_sessions,
                'attended_sessions': attended_sessions,
                'percentage': round(percentage, 2)
            })
        
        context = {
            'course': course,
            'report_data': report_data,
            'courses': Course.objects.all()
        }
        return render(request, 'attendance/admin_reports.html', context)
    
    courses = Course.objects.all()
    return render(request, 'attendance/admin_reports.html', {'courses': courses})

@login_required
@role_required(['admin'])
def create_student(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Student created successfully.")
            return redirect('dashboard')
    else:
        form = StudentCreationForm()
    return render(request, 'attendance/create_student.html', {'form': form})


@login_required
@role_required(['admin'])
def create_teacher(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher created successfully.")
            return redirect('dashboard')
    else:
        form = TeacherCreationForm()
    return render(request, 'attendance/create_teacher.html', {'form': form})

@login_required
@role_required(['admin'])
def assign_teacher_course(request):
    if request.method == 'POST':
        form = AssignTeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher assigned to course.')
            return redirect('dashboard')
    else:
        form = AssignTeacherForm()
    return render(request, 'attendance/assign_teacher.html', {'form': form})

@login_required
@role_required(['admin'])
def enroll_student_course(request):
    if request.method == 'POST':
        form = EnrollStudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student enrolled in course.')
            return redirect('dashboard')
    else:
        form = EnrollStudentForm()
    return render(request, 'attendance/enroll_student.html', {'form': form})

@login_required
@role_required(['admin'])
def create_department(request):
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Department created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_department.html', {'form': form})


@login_required
@role_required(['admin'])
def create_course(request):
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Course created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_course.html', {'form': form})


@login_required
@role_required(['admin'])
def create_batch(request):
    form = BatchForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Batch created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_batch.html', {'form': form})

@login_required
@role_required(['admin'])
def create_program(request):
    form = ProgramForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Program created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_program.html', {'form': form})

@login_required
@role_required(['admin'])
def create_academic_year(request):
    form = AcademicYearForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Academic year created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_academic_year.html', {'form': form})

@login_required
@role_required(['admin'])
def create_semester(request):
    form = SemesterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Semester created successfully.")
        return redirect('dashboard')
    return render(request, 'attendance/create_semester.html', {'form': form})

from django.http import JsonResponse


@login_required
@role_required(['admin'])
def get_students_by_batch(request):
    batch_id = request.GET.get('batch_id')
    students = User.objects.filter(studentprofile__batch_id=batch_id, role='student')
    student_data = [{'id': s.id, 'name': s.get_full_name()} for s in students]
    return JsonResponse({'students': student_data})

@login_required
@role_required(['admin'])
def get_courses_by_semester(request):
    semester_id = request.GET.get('semester_id')
    courses = Course.objects.filter(semester_id=semester_id)
    course_data = [{'id': c.id, 'name': f"{c.code} - {c.name}"} for c in courses]
    return JsonResponse({'courses': course_data})

@login_required
@role_required(['admin'])
def get_student_courses(request):
    student_id = request.GET.get('student_id')
    if student_id:
        enrolled_courses = Course.objects.filter(
            studentcourse__student_id=student_id
        ).values('id', 'code', 'name')
        return JsonResponse({'enrolled_courses': list(enrolled_courses)})
    return JsonResponse({'enrolled_courses': []})

@login_required
@role_required(['admin'])
def get_teacher_courses(request):
    teacher_id = request.GET.get('teacher_id')
    if teacher_id:
        assigned_courses = Course.objects.filter(
            teachercourse__teacher_id=teacher_id
        ).values('id', 'code', 'name')
        return JsonResponse({'assigned_courses': list(assigned_courses)})
    return JsonResponse({'assigned_courses': []})

@login_required
@role_required(['admin'])
def remove_student_course(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')
        try:
            enrollment = StudentCourse.objects.get(student_id=student_id, course_id=course_id)
            enrollment.delete()
            return JsonResponse({'success': True, 'message': 'Course removed successfully'})
        except StudentCourse.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Enrollment not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@role_required(['admin'])
def remove_teacher_course(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        course_id = request.POST.get('course_id')
        try:
            assignment = TeacherCourse.objects.get(teacher_id=teacher_id, course_id=course_id)
            assignment.delete()
            return JsonResponse({'success': True, 'message': 'Course assignment removed successfully'})
        except TeacherCourse.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Assignment not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

@login_required
@role_required(['admin'])
def bulk_enroll_students(request):
    form = BulkEnrollStudentsForm()

    if request.method == 'POST':
        form = BulkEnrollStudentsForm(request.POST)
        if form.is_valid():
            students = form.cleaned_data['students']
            courses = form.cleaned_data['courses']
            semester = form.cleaned_data['semester']
            academic_year = semester.academic_year

            for student in students:
                for course in courses:
                    StudentCourse.objects.get_or_create(
                        student=student,
                        course=course,
                        academic_year=academic_year
                    )
            messages.success(request, "Students enrolled successfully.")
            return redirect('dashboard')

    return render(request, 'attendance/bulk_enroll_students.html', {'form': form})

from django.core.paginator import Paginator

@login_required
@role_required(['admin'])
def department_list(request):
    departments = Department.objects.all().order_by('name')
    paginator = Paginator(departments, 10)  # 10 per page
    page = request.GET.get('page')
    departments_page = paginator.get_page(page)
    return render(request, 'attendance/department_list.html', {'departments': departments_page})

@login_required
@role_required(['admin'])
def update_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        messages.success(request, "Department updated.")
        return redirect('department_list')
    return render(request, 'attendance/update_department.html', {'form': form})

@login_required
@role_required(['admin'])
def delete_department(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, "Department deleted.")
        return redirect('department_list')
    return render(request, 'attendance/delete_confirm.html', {'object': department, 'type': 'Department'})

from django.db.models.query import QuerySet

def list_update_delete(request, model_or_queryset, Form, template, context_name, UpdateForm=None, search_fields=None):
    # Determine if input is a queryset or model
    if isinstance(model_or_queryset, QuerySet):
        queryset = model_or_queryset.order_by('id')
        Model = queryset.model  # extract model from queryset
    else:
        Model = model_or_queryset
        queryset = Model.objects.all().order_by('id')

    # Apply search filters
    search_query = request.GET.get('search', '').strip()
    if search_query and search_fields:
        from django.db.models import Q
        search_filter = Q()
        for field in search_fields:
            search_filter |= Q(**{f"{field}__icontains": search_query})
        queryset = queryset.filter(search_filter)

    # Apply additional filters based on model
    if Model.__name__ == 'User':
        # Filter by role if specified
        role_filter = request.GET.get('role', '').strip()
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        
        # Filter by batch for students
        batch_filter = request.GET.get('batch', '').strip()
        if batch_filter and 'student' in context_name:
            queryset = queryset.filter(studentprofile__batch_id=batch_filter)
    
    elif Model.__name__ == 'Course':
        # Filter by department
        dept_filter = request.GET.get('department', '').strip()
        if dept_filter:
            queryset = queryset.filter(department_id=dept_filter)
        
        # Filter by semester
        sem_filter = request.GET.get('semester', '').strip()
        if sem_filter:
            queryset = queryset.filter(semester_id=sem_filter)

    # Pagination
    page = Paginator(queryset, 10).get_page(request.GET.get('page'))

    # Use UpdateForm if provided, otherwise use the same Form
    ActualUpdateForm = UpdateForm if UpdateForm else Form

    # Process POST
    if request.method == 'POST':
        if 'update_id' in request.POST:
            inst = get_object_or_404(Model, pk=request.POST['update_id'])
            form = ActualUpdateForm(request.POST, instance=inst)
            if form.is_valid():
                form.save()
                messages.success(request, f"{Model.__name__} updated successfully.")
                return redirect(request.path)
            else:
                # Add form errors to context for modal display
                context = {
                    context_name: page,
                    'add_form': Form(),
                    'update_form': form,
                    'update_instance': inst,
                    'show_update_modal': True,
                    'search_query': search_query,
                }
                return render(request, template, context)
        elif 'delete_id' in request.POST:
            inst = get_object_or_404(Model, pk=request.POST['delete_id'])
            inst.delete()
            messages.success(request, f"{Model.__name__} deleted successfully.")
            return redirect(request.path)
        elif 'add' in request.POST:
            form = Form(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"{Model.__name__} created successfully.")
                return redirect(request.path)
            else:
                context = {
                    context_name: page,
                    'add_form': form,
                    'show_add_modal': True,
                    'search_query': search_query,
                }
                return render(request, template, context)

    # Prepare filter options for templates
    filter_options = {}
    if Model.__name__ == 'User':
        filter_options['batches'] = Batch.objects.all()
        filter_options['courses'] = Course.objects.all()  # Add courses for student/teacher management
    elif Model.__name__ == 'Course':
        filter_options['departments'] = Department.objects.all()
        filter_options['semesters'] = Semester.objects.all()

    context = {
        context_name: page,
        'add_form': Form(),
        'search_query': search_query,
        'filter_options': filter_options,
    }
    return render(request, template, context)


@login_required
@role_required(['admin'])
def program_list(request):
    return list_update_delete(request, Program, ProgramForm, 'attendance/program_list.html', 'programs', 
                            search_fields=['name', 'code'])

@login_required
@role_required(['admin'])
def batch_list(request):
    return list_update_delete(request, Batch, BatchForm, 'attendance/batch_list.html', 'batches',
                            search_fields=['year', 'department__name', 'program__name'])

@login_required
@role_required(['admin'])
def academic_year_list(request):
    return list_update_delete(request, AcademicYear, AcademicYearForm, 'attendance/academic_year_list.html', 'academic_years',
                            search_fields=['batch__year', 'start_year', 'end_year'])

@login_required
@role_required(['admin'])
def semester_list(request):
    return list_update_delete(request, Semester, SemesterForm, 'attendance/semester_list.html', 'semesters',
                            search_fields=['academic_year__batch__year', 'name', 'number'])

@login_required
@role_required(['admin'])
def course_list(request):
    return list_update_delete(request, Course, CourseForm, 'attendance/course_list.html', 'courses',
                            search_fields=['name', 'code', 'department__name'])

@login_required
@role_required(['admin'])
def student_list(request):
    queryset = User.objects.filter(role='student')
    return list_update_delete(request, queryset, StudentCreationForm, 'attendance/student_list.html', 'students', 
                            StudentUpdateForm, search_fields=['username', 'first_name', 'last_name', 'email', 'student_id'])

@login_required
@role_required(['admin'])
def teacher_list(request):
    queryset = User.objects.filter(role='teacher')
    return list_update_delete(request, queryset, TeacherCreationForm, 'attendance/teacher_list.html', 'teachers', 
                            TeacherUpdateForm, search_fields=['username', 'first_name', 'last_name', 'email', 'employee_id'])

@login_required
@role_required(['admin'])
def department_list(request):
    return list_update_delete(request, Department, DepartmentForm, 'attendance/department_list.html', 'departments',
                            search_fields=['name', 'code'])

@login_required
@role_required(['admin'])
def teacher_course_assignments(request):
    return list_update_delete(request, TeacherCourse, AssignTeacherForm, 'attendance/teacher_course_assignments.html', 'assignments', 
                            TeacherCourseUpdateForm, search_fields=['teacher__username', 'teacher__first_name', 'course__name', 'course__code'])

@login_required
@role_required(['admin'])
def student_course_enrollments(request):
    return list_update_delete(request, StudentCourse, EnrollStudentForm, 'attendance/student_course_enrollments.html', 'enrollments',
                            search_fields=['student__username', 'student__first_name', 'course__name', 'course__code'])
