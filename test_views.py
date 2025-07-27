from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages import get_messages
from sams.models import *
import json

User = get_user_model()

class LoginRequiredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_login_required_views(self):
        # Test dashboard view
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test teacher courses view
        response = self.client.get(reverse('teacher_courses'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test student attendance view
        response = self.client.get(reverse('student_attendance'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            email='admin1@example.com',
            role='admin'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.batch = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            name='First Semester'
        )
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=4,
            department=self.department,
            semester=self.semester
        )
        # Login as admin
        self.client.login(username='admin1', password='password123')

    def test_admin_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/admin_dashboard.html')
        # Check context data
        self.assertIn('total_students', response.context)
        self.assertIn('total_teachers', response.context)
        self.assertIn('total_courses', response.context)
        self.assertIn('total_departments', response.context)

    def test_create_student_view_get(self):
        response = self.client.get(reverse('create_student'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/create_student.html')

    def test_create_student_view_post_valid(self):
        form_data = {
            'username': 'newstudent',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'student_id': 'S12345',
            'phone': '1234567890',
            'batch': self.batch.id
        }
        response = self.client.post(reverse('create_student'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newstudent').exists())

    def test_create_teacher_view_get(self):
        response = self.client.get(reverse('create_teacher'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/create_teacher.html')

    def test_create_teacher_view_post_valid(self):
        form_data = {
            'username': 'newteacher',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com',
            'employee_id': 'T12345',
            'phone': '1234567890'
        }
        response = self.client.post(reverse('create_teacher'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newteacher').exists())

    def test_create_department_view(self):
        form_data = {
            'name': 'Mathematics',
            'code': 'MATH'
        }
        response = self.client.post(reverse('create_department'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Department.objects.filter(code='MATH').exists())

    def test_create_course_view(self):
        form_data = {
            'name': 'Data Structures',
            'code': 'CS102',
            'credits': 3,
            'department': self.department.id,
            'semester': self.semester.id
        }
        response = self.client.post(reverse('create_course'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Course.objects.filter(code='CS102').exists())

    def test_assign_teacher_course_view(self):
        teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        form_data = {
            'teacher': teacher.id,
            'course': self.course.id,
            'academic_year': self.academic_year.id
        }
        response = self.client.post(reverse('assign_teacher_course'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(TeacherCourse.objects.filter(teacher=teacher, course=self.course).exists())

    def test_enroll_student_course_view(self):
        student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        form_data = {
            'student': student.id,
            'course': self.course.id,
            'academic_year': self.academic_year.id
        }
        response = self.client.post(reverse('enroll_student_course'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(StudentCourse.objects.filter(student=student, course=self.course).exists())

    def test_admin_reports_view(self):
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/admin_reports.html')

    def test_admin_reports_with_course_filter(self):
        response = self.client.get(reverse('admin_reports'), {'course_id': self.course.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('course', response.context)
        self.assertEqual(response.context['course'], self.course)

class TeacherViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create teacher user
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            email='teacher1@example.com',
            role='teacher'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.batch = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            name='First Semester'
        )
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=4,
            department=self.department,
            semester=self.semester
        )
        self.teacher_course = TeacherCourse.objects.create(
            teacher=self.teacher,
            course=self.course,
            academic_year=self.academic_year
        )
        # Login as teacher
        self.client.login(username='teacher1', password='password123')

    def test_teacher_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/teacher_dashboard.html')
        self.assertIn('courses', response.context)

    def test_teacher_courses_view(self):
        response = self.client.get(reverse('teacher_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/teacher_courses.html')
        self.assertIn('courses', response.context)

    def test_mark_attendance_view_get(self):
        response = self.client.get(reverse('mark_attendance', args=[self.teacher_course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/mark_attendance.html')

    def test_mark_attendance_view_post(self):
        # Create a student enrolled in the course
        student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        StudentCourse.objects.create(
            student=student,
            course=self.course,
            academic_year=self.academic_year
        )
        
        form_data = {
            'date': timezone.now().date(),
            'start_time': '09:00',
            'end_time': '10:00',
            'topic': 'Introduction to Python',
            f'attendance_{student.id}': 'present'
        }
        response = self.client.post(reverse('mark_attendance', args=[self.teacher_course.id]), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check if attendance session was created
        self.assertTrue(AttendanceSession.objects.filter(course=self.course, teacher=self.teacher).exists())
        # Check if attendance was marked
        self.assertTrue(Attendance.objects.filter(student=student, status='present').exists())

    def test_attendance_history_view(self):
        response = self.client.get(reverse('attendance_history', args=[self.teacher_course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/attendance_history.html')

class StudentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create student user
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            email='student1@example.com',
            role='student'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.batch = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            name='First Semester'
        )
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=4,
            department=self.department,
            semester=self.semester
        )
        self.student_course = StudentCourse.objects.create(
            student=self.student,
            course=self.course,
            academic_year=self.academic_year
        )
        # Login as student
        self.client.login(username='student1', password='password123')

    def test_student_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/student_dashboard.html')
        self.assertIn('courses', response.context)
        self.assertIn('semester_courses', response.context)

    def test_student_attendance_view(self):
        response = self.client.get(reverse('student_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/student_attendance.html')
        self.assertIn('attendance_data', response.context)

class RolePermissionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            role='admin'
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )

    def test_admin_only_views_with_teacher(self):
        self.client.login(username='teacher1', password='password123')
        response = self.client.get(reverse('create_student'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("don't have permission" in str(m) for m in messages))

    def test_admin_only_views_with_student(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('create_teacher'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

    def test_teacher_only_views_with_student(self):
        self.client.login(username='student1', password='password123')
        response = self.client.get(reverse('teacher_courses'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

    def test_student_only_views_with_teacher(self):
        self.client.login(username='teacher1', password='password123')
        response = self.client.get(reverse('student_attendance'))
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

class AjaxViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            role='admin'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.batch = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            name='First Semester'
        )
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=4,
            department=self.department,
            semester=self.semester
        )
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        StudentProfile.objects.create(user=self.student, batch=self.batch)
        
        self.client.login(username='admin1', password='password123')

    def test_get_students_by_batch(self):
        response = self.client.get(reverse('ajax_get_students_by_batch'), {'batch_id': self.batch.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('students', data)
        self.assertEqual(len(data['students']), 1)
        self.assertEqual(data['students'][0]['id'], self.student.id)

    def test_get_courses_by_semester(self):
        response = self.client.get(reverse('ajax_get_courses_by_semester'), {'semester_id': self.semester.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('courses', data)
        self.assertEqual(len(data['courses']), 1)
        self.assertEqual(data['courses'][0]['id'], self.course.id)

    def test_get_student_courses(self):
        StudentCourse.objects.create(
            student=self.student,
            course=self.course,
            academic_year=self.academic_year
        )
        response = self.client.get(reverse('ajax_get_student_courses'), {'student_id': self.student.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('enrolled_courses', data)
        self.assertEqual(len(data['enrolled_courses']), 1)

    def test_remove_student_course(self):
        student_course = StudentCourse.objects.create(
            student=self.student,
            course=self.course,
            academic_year=self.academic_year
        )
        response = self.client.post(reverse('ajax_remove_student_course'), {
            'student_id': self.student.id,
            'course_id': self.course.id
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(StudentCourse.objects.filter(id=student_course.id).exists())

class ListViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            role='admin'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.client.login(username='admin1', password='password123')

    def test_department_list_view(self):
        response = self.client.get(reverse('department_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/department_list.html')
        self.assertIn('departments', response.context)

    def test_program_list_view(self):
        response = self.client.get(reverse('program_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/program_list.html')
        self.assertIn('programs', response.context)

    def test_course_list_view(self):
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/course_list.html')
        self.assertIn('courses', response.context)

    def test_student_list_view(self):
        response = self.client.get(reverse('student_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/student_list.html')
        self.assertIn('students', response.context)

    def test_teacher_list_view(self):
        response = self.client.get(reverse('teacher_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/teacher_list.html')
        self.assertIn('teachers', response.context)

    def test_list_view_with_search(self):
        response = self.client.get(reverse('department_list'), {'search': 'Computer'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('search_query', response.context)
        self.assertEqual(response.context['search_query'], 'Computer')

class BulkEnrollViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            role='admin'
        )
        # Create test data
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )
        self.batch = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )
        self.semester = Semester.objects.create(
            academic_year=self.academic_year,
            number=1,
            name='First Semester'
        )
        self.course = Course.objects.create(
            name='Introduction to Programming',
            code='CS101',
            credits=4,
            department=self.department,
            semester=self.semester
        )
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        self.client.login(username='admin1', password='password123')

    def test_bulk_enroll_students_view_get(self):
        response = self.client.get(reverse('bulk_enroll_students'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'attendance/bulk_enroll_students.html')

    def test_bulk_enroll_students_view_post(self):
        form_data = {
            'batch': self.batch.id,
            'semester': self.semester.id,
            'students': [self.student.id],
            'courses': [self.course.id]
        }
        response = self.client.post(reverse('bulk_enroll_students'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(StudentCourse.objects.filter(student=self.student, course=self.course).exists())