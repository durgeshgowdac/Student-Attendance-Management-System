from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import *

User = get_user_model()

class BasicSAMSTest(TestCase):
    """Basic tests for SAMS functionality"""
    
    def setUp(self):
        """Set up test data"""
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

    def test_user_creation(self):
        """Test that users are created with correct roles"""
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.teacher.role, 'teacher')
        self.assertEqual(self.student.role, 'student')

    def test_user_authentication(self):
        """Test user authentication"""
        self.assertTrue(self.admin.check_password('admin123'))
        self.assertTrue(self.teacher.check_password('teacher123'))
        self.assertTrue(self.student.check_password('student123'))

    def test_login_redirect(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

class ModelRelationshipTest(TestCase):
    """Test model relationships and constraints"""
    
    def setUp(self):
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

    def test_department_creation(self):
        """Test department creation"""
        self.assertEqual(self.department.name, 'Computer Science')
        self.assertEqual(str(self.department), 'CS - Computer Science')

    def test_batch_relationships(self):
        """Test batch relationships with department and program"""
        self.assertEqual(self.batch.department, self.department)
        self.assertEqual(self.batch.program, self.program)
        self.assertEqual(str(self.batch), 'BTech - CS - Batch 2023-2025')

class AttendanceFlowTest(TestCase):
    """Test basic attendance flow"""
    
    def setUp(self):
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

    def test_attendance_session_creation(self):
        """Test creating an attendance session"""
        session = AttendanceSession.objects.create(
            course=self.course,
            teacher=self.teacher,
            date=timezone.now().date(),
            start_time='09:00',
            end_time='10:00',
            academic_year=self.academic_year,
            topic='Test Topic'
        )
        
        self.assertEqual(session.course, self.course)
        self.assertEqual(session.teacher, self.teacher)
        self.assertEqual(session.topic, 'Test Topic')

    def test_attendance_marking(self):
        """Test marking attendance for a student"""
        session = AttendanceSession.objects.create(
            course=self.course,
            teacher=self.teacher,
            date=timezone.now().date(),
            start_time='09:00',
            end_time='10:00',
            academic_year=self.academic_year
        )
        
        attendance = Attendance.objects.create(
            session=session,
            student=self.student,
            status='present',
            marked_by=self.teacher
        )
        
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.student, self.student)
        self.assertEqual(attendance.marked_by, self.teacher)
