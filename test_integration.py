from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from sams.models import *
import json

User = get_user_model()

class AttendanceWorkflowIntegrationTest(TestCase):
    """Test the complete attendance workflow from admin setup to student viewing"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='teacher123',
            role='teacher',
            first_name='John',
            last_name='Doe',
            employee_id='T001'
        )
        self.student = User.objects.create_user(
            username='student1',
            password='student123',
            role='student',
            first_name='Jane',
            last_name='Smith',
            student_id='S001'
        )

    def test_complete_attendance_workflow(self):
        """Test the complete workflow from setup to attendance marking"""
        
        # Step 1: Admin creates department
        self.client.login(username='admin', password='admin123')
        dept_data = {'name': 'Computer Science', 'code': 'CS'}
        response = self.client.post(reverse('create_department'), data=dept_data)
        self.assertEqual(response.status_code, 302)
        department = Department.objects.get(code='CS')
        
        # Step 2: Admin creates program
        prog_data = {'name': 'Bachelor of Technology', 'code': 'BTech'}
        response = self.client.post(reverse('create_program'), data=prog_data)
        self.assertEqual(response.status_code, 302)
        program = Program.objects.get(code='BTech')
        
        # Step 3: Admin creates batch
        batch_data = {
            'year': '2023-2025',
            'department': department.id,
            'program': program.id
        }
        response = self.client.post(reverse('create_batch'), data=batch_data)
        self.assertEqual(response.status_code, 302)
        batch = Batch.objects.get(year='2023-2025')
        
        # Step 4: Admin creates academic year
        ay_data = {
            'batch': batch.id,
            'start_year': 2023,
            'end_year': 2024
        }
        response = self.client.post(reverse('create_academic_year'), data=ay_data)
        self.assertEqual(response.status_code, 302)
        academic_year = AcademicYear.objects.get(start_year=2023, end_year=2024)
        
        # Step 5: Admin creates semester
        sem_data = {
            'academic_year': academic_year.id,
            'number': 1,
            'name': 'First Semester'
        }
        response = self.client.post(reverse('create_semester'), data=sem_data)
        self.assertEqual(response.status_code, 302)
        semester = Semester.objects.get(number=1, academic_year=academic_year)
        
        # Step 6: Admin creates course
        course_data = {
            'name': 'Introduction to Programming',
            'code': 'CS101',
            'credits': 4,
            'department': department.id,
            'semester': semester.id
        }
        response = self.client.post(reverse('create_course'), data=course_data)
        self.assertEqual(response.status_code, 302)
        course = Course.objects.get(code='CS101')
        
        # Step 7: Admin assigns teacher to course
        assign_data = {
            'teacher': self.teacher.id,
            'course': course.id,
            'academic_year': academic_year.id
        }
        response = self.client.post(reverse('assign_teacher_course'), data=assign_data)
        self.assertEqual(response.status_code, 302)
        teacher_course = TeacherCourse.objects.get(teacher=self.teacher, course=course)
        
        # Step 8: Admin enrolls student in course
        enroll_data = {
            'student': self.student.id,
            'course': course.id,
            'academic_year': academic_year.id
        }
        response = self.client.post(reverse('enroll_student_course'), data=enroll_data)
        self.assertEqual(response.status_code, 302)
        student_course = StudentCourse.objects.get(student=self.student, course=course)
        
        # Step 9: Teacher logs in and marks attendance
        self.client.login(username='teacher1', password='teacher123')
        
        # Teacher views their courses
        response = self.client.get(reverse('teacher_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS101')
        
        # Teacher marks attendance
        attendance_data = {
            'date': timezone.now().date(),
            'start_time': '09:00',
            'end_time': '10:00',
            'topic': 'Introduction to Python',
            f'attendance_{self.student.id}': 'present'
        }
        response = self.client.post(
            reverse('mark_attendance', args=[teacher_course.id]), 
            data=attendance_data
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify attendance session was created
        session = AttendanceSession.objects.get(course=course, teacher=self.teacher)
        self.assertEqual(session.topic, 'Introduction to Python')
        
        # Verify attendance was marked
        attendance = Attendance.objects.get(session=session, student=self.student)
        self.assertEqual(attendance.status, 'present')
        
        # Step 10: Student logs in and views attendance
        self.client.login(username='student1', password='student123')
        
        response = self.client.get(reverse('student_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CS101')
        self.assertContains(response, 'Present')
        
        # Step 11: Admin views reports
        self.client.login(username='admin', password='admin123')
        
        response = self.client.get(reverse('admin_reports'), {'course_id': course.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane Smith')  # Student's full name
        self.assertContains(response, '100.0')  # 100% attendance

class BulkOperationsIntegrationTest(TestCase):
    """Test bulk operations like bulk enrollment"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        # Create basic structure
        self.department = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BTech', code='BTech')
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
            name='Sem 1'
        )
        
        # Create multiple students
        self.students = []
        for i in range(5):
            student = User.objects.create_user(
                username=f'student{i+1}',
                password='password123',
                role='student',
                student_id=f'S00{i+1}'
            )
            self.students.append(student)
        
        # Create multiple courses
        self.courses = []
        for i in range(3):
            course = Course.objects.create(
                name=f'Course {i+1}',
                code=f'CS10{i+1}',
                credits=3,
                department=self.department,
                semester=self.semester
            )
            self.courses.append(course)
        
        self.client.login(username='admin', password='admin123')

    def test_bulk_enrollment(self):
        """Test bulk enrollment of students to courses"""
        
        form_data = {
            'batch': self.batch.id,
            'semester': self.semester.id,
            'students': [s.id for s in self.students],
            'courses': [c.id for c in self.courses]
        }
        
        response = self.client.post(reverse('bulk_enroll_students'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # Verify all students are enrolled in all courses
        for student in self.students:
            for course in self.courses:
                self.assertTrue(
                    StudentCourse.objects.filter(
                        student=student,
                        course=course,
                        academic_year=self.academic_year
                    ).exists()
                )

class DataIntegrityIntegrationTest(TransactionTestCase):
    """Test data integrity and constraint violations"""
    
    def setUp(self):
        self.department = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BTech', code='BTech')

    def test_unique_constraints(self):
        """Test that unique constraints are properly enforced"""
        
        # Test duplicate department code
        with self.assertRaises(Exception):
            with transaction.atomic():
                Department.objects.create(name='Computer Engineering', code='CS')
        
        # Test duplicate program code
        with self.assertRaises(Exception):
            with transaction.atomic():
                Program.objects.create(name='Bachelor of Engineering', code='BTech')
        
        # Test duplicate user student_id
        User.objects.create_user(
            username='student1',
            password='password123',
            role='student',
            student_id='S001'
        )
        
        with self.assertRaises(Exception):
            with transaction.atomic():
                User.objects.create_user(
                    username='student2',
                    password='password123',
                    role='student',
                    student_id='S001'  # Duplicate student_id
                )

class PermissionIntegrationTest(TestCase):
    """Test role-based permissions across the system"""
    
    def setUp(self):
        self.client = Client()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacher123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            password='student123',
            role='student'
        )
        
        # Create test data
        self.department = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BTech', code='BTech')
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
            number=1
        )
        self.course = Course.objects.create(
            name='Test Course',
            code='CS101',
            credits=3,
            department=self.department,
            semester=self.semester
        )

    def test_admin_permissions(self):
        """Test that admin can access all admin-only views"""
        self.client.login(username='admin', password='admin123')
        
        admin_urls = [
            'create_student',
            'create_teacher',
            'create_department',
            'create_course',
            'assign_teacher_course',
            'enroll_student_course',
            'admin_reports',
            'bulk_enroll_students',
            'department_list',
            'student_list',
            'teacher_list'
        ]
        
        for url_name in admin_urls:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [200, 302])  # 200 for GET, 302 for redirect after POST

    def test_teacher_permissions(self):
        """Test that teacher can only access teacher-specific views"""
        self.client.login(username='teacher', password='teacher123')
        
        # Teacher should be able to access these
        teacher_urls = ['teacher_courses']
        for url_name in teacher_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
        
        # Teacher should NOT be able to access admin views
        admin_urls = ['create_student', 'create_teacher', 'admin_reports']
        for url_name in admin_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

    def test_student_permissions(self):
        """Test that student can only access student-specific views"""
        self.client.login(username='student', password='student123')
        
        # Student should be able to access these
        student_urls = ['student_attendance']
        for url_name in student_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 200)
        
        # Student should NOT be able to access admin or teacher views
        restricted_urls = ['create_student', 'teacher_courses', 'admin_reports']
        for url_name in restricted_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)  # Redirect due to permission denied

class AttendanceCalculationIntegrationTest(TestCase):
    """Test attendance percentage calculations"""
    
    def setUp(self):
        self.client = Client()
        
        # Create basic structure
        self.department = Department.objects.create(name='CS', code='CS')
        self.program = Program.objects.create(name='BTech', code='BTech')
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
            number=1
        )
        self.course = Course.objects.create(
            name='Test Course',
            code='CS101',
            credits=3,
            department=self.department,
            semester=self.semester
        )
        
        # Create users
        self.teacher = User.objects.create_user(
            username='teacher',
            password='teacher123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student',
            password='student123',
            role='student'
        )
        
        # Create assignments
        TeacherCourse.objects.create(
            teacher=self.teacher,
            course=self.course,
            academic_year=self.academic_year
        )
        StudentCourse.objects.create(
            student=self.student,
            course=self.course,
            academic_year=self.academic_year
        )

    def test_attendance_percentage_calculation(self):
        """Test that attendance percentages are calculated correctly"""
        
        # Create 5 attendance sessions
        sessions = []
        for i in range(5):
            start_hour = 9 + i
            end_hour = 10 + i
            session = AttendanceSession.objects.create(
                course=self.course,
                teacher=self.teacher,
                date=timezone.now().date(),
                start_time=f'{start_hour:02d}:00',
                end_time=f'{end_hour:02d}:00',
                academic_year=self.academic_year,
                topic=f'Topic {i+1}'
            )
            sessions.append(session)
        
        # Mark attendance: present for 3 sessions, absent for 2
        statuses = ['present', 'present', 'absent', 'present', 'absent']
        for session, status in zip(sessions, statuses):
            Attendance.objects.create(
                session=session,
                student=self.student,
                status=status,
                marked_by=self.teacher
            )
        
        # Login as student and check dashboard
        self.client.login(username='student', password='student123')
        response = self.client.get(reverse('dashboard'))
        
        # Should show 60% attendance (3 out of 5)
        self.assertContains(response, '60.0')

class SearchAndFilterIntegrationTest(TestCase):
    """Test search and filter functionality"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        # Create test data
        self.dept1 = Department.objects.create(name='Computer Science', code='CS')
        self.dept2 = Department.objects.create(name='Mathematics', code='MATH')
        
        self.student1 = User.objects.create_user(
            username='john_doe',
            password='password123',
            role='student',
            first_name='John',
            last_name='Doe'
        )
        self.student2 = User.objects.create_user(
            username='jane_smith',
            password='password123',
            role='student',
            first_name='Jane',
            last_name='Smith'
        )
        
        self.client.login(username='admin', password='admin123')

    def test_department_search(self):
        """Test searching departments"""
        response = self.client.get(reverse('department_list'), {'search': 'Computer'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Computer Science')
        self.assertNotContains(response, 'Mathematics')

    def test_student_search(self):
        """Test searching students"""
        response = self.client.get(reverse('student_list'), {'search': 'John'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'john_doe')
        self.assertNotContains(response, 'jane_smith')