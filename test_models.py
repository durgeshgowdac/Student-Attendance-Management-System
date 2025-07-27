from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from sams.models import *
import datetime

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            email='student1@example.com',
            first_name='Student',
            last_name='One',
            role='student',
            student_id='S12345'
        )
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            email='teacher1@example.com',
            first_name='Teacher',
            last_name='One',
            role='teacher',
            employee_id='T12345'
        )
        self.admin = User.objects.create_user(
            username='admin1',
            password='password123',
            email='admin1@example.com',
            first_name='Admin',
            last_name='One',
            role='admin'
        )

    def test_user_creation(self):
        self.assertEqual(self.student.role, 'student')
        self.assertEqual(self.teacher.role, 'teacher')
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(self.student.student_id, 'S12345')
        self.assertEqual(self.teacher.employee_id, 'T12345')

    def test_user_str_method(self):
        self.assertEqual(str(self.student), 'student1 (student)')
        self.assertEqual(str(self.teacher), 'teacher1 (teacher)')

    def test_unique_constraints(self):
        from django.db import transaction
        
        # Test unique student_id
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username='student2',
                    password='password123',
                    role='student',
                    student_id='S12345'  # Duplicate student_id
                )
        
        # Test unique employee_id
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                User.objects.create_user(
                    username='teacher2',
                    password='password123',
                    role='teacher',
                    employee_id='T12345'  # Duplicate employee_id
                )

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS',
            head=self.teacher
        )

    def test_department_creation(self):
        self.assertEqual(self.department.name, 'Computer Science')
        self.assertEqual(self.department.code, 'CS')
        self.assertEqual(self.department.head, self.teacher)

    def test_department_str_method(self):
        self.assertEqual(str(self.department), 'CS - Computer Science')

    def test_unique_code_constraint(self):
        with self.assertRaises(IntegrityError):
            Department.objects.create(
                name='Computer Engineering',
                code='CS'  # Duplicate code
            )

class ProgramModelTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )

    def test_program_creation(self):
        self.assertEqual(self.program.name, 'Bachelor of Technology')
        self.assertEqual(self.program.code, 'BTech')

    def test_program_str_method(self):
        self.assertEqual(str(self.program), 'BTech - Bachelor of Technology')

    def test_unique_constraints(self):
        with self.assertRaises(IntegrityError):
            Program.objects.create(
                name='Bachelor of Technology',  # Duplicate name
                code='BT'
            )

class BatchModelTest(TestCase):
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

    def test_batch_creation(self):
        self.assertEqual(self.batch.year, '2023-2025')
        self.assertEqual(self.batch.department, self.department)
        self.assertEqual(self.batch.program, self.program)

    def test_batch_str_method(self):
        self.assertEqual(str(self.batch), 'BTech - CS - Batch 2023-2025')

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            Batch.objects.create(
                year='2023-2025',  # Same combination
                department=self.department,
                program=self.program
            )

class AcademicYearModelTest(TestCase):
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
        self.academic_year = AcademicYear.objects.create(
            batch=self.batch,
            start_year=2023,
            end_year=2024
        )

    def test_academic_year_creation(self):
        self.assertEqual(self.academic_year.batch, self.batch)
        self.assertEqual(self.academic_year.start_year, 2023)
        self.assertEqual(self.academic_year.end_year, 2024)

    def test_academic_year_str_method(self):
        self.assertEqual(str(self.academic_year), '2023-2024 (2023-2025)')

class SemesterModelTest(TestCase):
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

    def test_semester_creation(self):
        self.assertEqual(self.semester.academic_year, self.academic_year)
        self.assertEqual(self.semester.number, 1)
        self.assertEqual(self.semester.name, 'First Semester')

    def test_semester_str_method(self):
        self.assertEqual(str(self.semester), '2023-2024 (2023-2025) - Sem 1')

    def test_semester_number_validation(self):
        # Test invalid semester number (should be 1 or 2)
        with self.assertRaises(ValidationError):
            semester = Semester(
                academic_year=self.academic_year,
                number=3,  # Invalid number
                name='Third Semester'
            )
            semester.full_clean()

class CourseModelTest(TestCase):
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

    def test_course_creation(self):
        self.assertEqual(self.course.name, 'Introduction to Programming')
        self.assertEqual(self.course.code, 'CS101')
        self.assertEqual(self.course.credits, 4)
        self.assertEqual(self.course.department, self.department)
        self.assertEqual(self.course.semester, self.semester)

    def test_course_str_method(self):
        self.assertEqual(str(self.course), 'CS101 - Introduction to Programming')

    def test_unique_code_constraint(self):
        with self.assertRaises(IntegrityError):
            Course.objects.create(
                name='Advanced Programming',
                code='CS101',  # Duplicate code
                credits=3,
                department=self.department,
                semester=self.semester
            )

class StudentProfileModelTest(TestCase):
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
        self.student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            batch=self.batch
        )

    def test_student_profile_creation(self):
        self.assertEqual(self.student_profile.user, self.student)
        self.assertEqual(self.student_profile.batch, self.batch)

    def test_student_profile_str_method(self):
        self.assertEqual(str(self.student_profile), 'student1 - BTech - CS - Batch 2023-2025')

class TeacherCourseModelTest(TestCase):
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
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        self.teacher_course = TeacherCourse.objects.create(
            teacher=self.teacher,
            course=self.course,
            academic_year=self.academic_year
        )

    def test_teacher_course_creation(self):
        self.assertEqual(self.teacher_course.teacher, self.teacher)
        self.assertEqual(self.teacher_course.course, self.course)
        self.assertEqual(self.teacher_course.academic_year, self.academic_year)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            TeacherCourse.objects.create(
                teacher=self.teacher,
                course=self.course,
                academic_year=self.academic_year
            )

class StudentCourseModelTest(TestCase):
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
        self.student_course = StudentCourse.objects.create(
            student=self.student,
            course=self.course,
            academic_year=self.academic_year
        )

    def test_student_course_creation(self):
        self.assertEqual(self.student_course.student, self.student)
        self.assertEqual(self.student_course.course, self.course)
        self.assertEqual(self.student_course.academic_year, self.academic_year)
        self.assertIsNotNone(self.student_course.enrolled_date)

    def test_student_course_str_method(self):
        self.assertEqual(str(self.student_course), 'student1 - CS101')

class AttendanceSessionModelTest(TestCase):
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
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        self.session = AttendanceSession.objects.create(
            course=self.course,
            teacher=self.teacher,
            date=timezone.now().date(),
            start_time='09:00',
            end_time='10:00',
            academic_year=self.academic_year,
            topic='Introduction to Python'
        )

    def test_attendance_session_creation(self):
        self.assertEqual(self.session.course, self.course)
        self.assertEqual(self.session.teacher, self.teacher)
        self.assertEqual(self.session.academic_year, self.academic_year)
        self.assertEqual(self.session.topic, 'Introduction to Python')

    def test_attendance_session_str_method(self):
        expected = f"CS101 - {self.session.date} (09:00)"
        self.assertEqual(str(self.session), expected)

class AttendanceModelTest(TestCase):
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
        self.session = AttendanceSession.objects.create(
            course=self.course,
            teacher=self.teacher,
            date=timezone.now().date(),
            start_time='09:00',
            end_time='10:00',
            academic_year=self.academic_year,
            topic='Introduction to Python'
        )
        self.attendance = Attendance.objects.create(
            session=self.session,
            student=self.student,
            status='present',
            marked_by=self.teacher
        )

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.session, self.session)
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.status, 'present')
        self.assertEqual(self.attendance.marked_by, self.teacher)
        self.assertIsNotNone(self.attendance.marked_at)

    def test_attendance_str_method(self):
        expected = f"student1 - CS101 - {self.session.date} (09:00) - present"
        self.assertEqual(str(self.attendance), expected)

    def test_unique_together_constraint(self):
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                session=self.session,
                student=self.student,  # Same session and student
                status='absent',
                marked_by=self.teacher
            )