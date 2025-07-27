from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from sams.forms import *
from sams.models import *

User = get_user_model()

class DeduplicationMixinTest(TestCase):
    def test_deduplication_mixin_save(self):
        """Test that DeduplicationMixin handles IntegrityError correctly"""
        # Create a form with DeduplicationMixin
        class TestForm(DeduplicationMixin, forms.ModelForm):
            class Meta:
                model = Department
                fields = ['name', 'code']
        
        # Create a department
        Department.objects.create(name='Computer Science', code='CS')
        
        # Try to create another department with the same code
        form = TestForm({
            'name': 'Computer Engineering',
            'code': 'CS'  # Duplicate code
        })
        
        self.assertTrue(form.is_valid())
        
        # Should raise IntegrityError and add form error
        with self.assertRaises(IntegrityError):
            form.save()
        
        self.assertIn('Duplicate entry already exists.', form.non_field_errors())
        
    def test_deduplication_mixin_save_no_error(self):
        """Test that DeduplicationMixin works correctly when no error occurs"""
        # Create a form with DeduplicationMixin
        class TestForm(DeduplicationMixin, forms.ModelForm):
            class Meta:
                model = Department
                fields = ['name', 'code']
        
        # Create a department with unique code
        form = TestForm({
            'name': 'Computer Science',
            'code': 'CS1'  # Unique code
        })
        
        self.assertTrue(form.is_valid())
        department = form.save()
        
        # Verify department was created
        self.assertEqual(department.name, 'Computer Science')
        self.assertEqual(department.code, 'CS1')
        self.assertTrue(Department.objects.filter(code='CS1').exists())

class BootstrapFormMixinTest(TestCase):
    def test_bootstrap_form_mixin(self):
        """Test that BootstrapFormMixin adds Bootstrap classes to form fields"""
        class TestForm(BootstrapFormMixin, forms.Form):
            text_field = forms.CharField()
            email_field = forms.EmailField()
            number_field = forms.IntegerField()
            select_field = forms.ChoiceField(choices=[('1', 'One'), ('2', 'Two')])
            multi_select_field = forms.MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        
        form = TestForm()
        
        # Check that form fields have Bootstrap classes
        self.assertIn('form-control', form.fields['text_field'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['email_field'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['number_field'].widget.attrs['class'])
        self.assertIn('form-select', form.fields['select_field'].widget.attrs['class'])
        self.assertIn('form-select', form.fields['multi_select_field'].widget.attrs['class'])
        
    def test_bootstrap_form_mixin_with_existing_classes(self):
        """Test that BootstrapFormMixin preserves existing classes"""
        class TestForm(BootstrapFormMixin, forms.Form):
            text_field = forms.CharField(widget=forms.TextInput(attrs={'class': 'existing-class'}))
        
        form = TestForm()
        
        # Check that form field has both existing and Bootstrap classes
        self.assertIn('existing-class', form.fields['text_field'].widget.attrs['class'])
        self.assertIn('form-control', form.fields['text_field'].widget.attrs['class'])

class StudentCreationFormTest(TestCase):
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

    def test_student_creation_form_valid(self):
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
        form = StudentCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_student_creation_form_password_mismatch(self):
        form_data = {
            'username': 'newstudent',
            'password1': 'complex_password123',
            'password2': 'different_password',
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstudent@example.com',
            'student_id': 'S12345',
            'phone': '1234567890',
            'batch': self.batch.id
        }
        form = StudentCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match.', form.non_field_errors())

    def test_student_creation_form_missing_required_fields(self):
        form_data = {
            'username': 'newstudent',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
        }
        form = StudentCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_student_creation_form_save(self):
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
        form = StudentCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.role, 'student')
        self.assertTrue(user.check_password('complex_password123'))
        self.assertTrue(hasattr(user, 'studentprofile'))
        self.assertEqual(user.studentprofile.batch, self.batch)

class TeacherCreationFormTest(TestCase):
    def test_teacher_creation_form_valid(self):
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
        form = TeacherCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_teacher_creation_form_password_mismatch(self):
        form_data = {
            'username': 'newteacher',
            'password1': 'complex_password123',
            'password2': 'different_password',
            'first_name': 'New',
            'last_name': 'Teacher',
            'email': 'newteacher@example.com',
            'employee_id': 'T12345',
            'phone': '1234567890'
        }
        form = TeacherCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_teacher_creation_form_save(self):
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
        form = TeacherCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        user = form.save()
        self.assertEqual(user.role, 'teacher')
        self.assertTrue(user.check_password('complex_password123'))

class DepartmentFormTest(TestCase):
    def test_department_form_valid(self):
        form_data = {
            'name': 'Computer Science',
            'code': 'CS'
        }
        form = DepartmentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_department_form_missing_required_fields(self):
        form_data = {
            'name': 'Computer Science'
        }
        form = DepartmentForm(data=form_data)
        self.assertFalse(form.is_valid())

class ProgramFormTest(TestCase):
    def test_program_form_valid(self):
        form_data = {
            'name': 'Bachelor of Technology',
            'code': 'BTech'
        }
        form = ProgramForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_program_form_missing_required_fields(self):
        form_data = {
            'name': 'Bachelor of Technology'
        }
        form = ProgramForm(data=form_data)
        self.assertFalse(form.is_valid())

class BatchFormTest(TestCase):
    def setUp(self):
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        self.program = Program.objects.create(
            name='Bachelor of Technology',
            code='BTech'
        )

    def test_batch_form_valid(self):
        form_data = {
            'year': '2023-2025',
            'department': self.department.id,
            'program': self.program.id
        }
        form = BatchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_batch_form_missing_required_fields(self):
        form_data = {
            'year': '2023-2025'
        }
        form = BatchForm(data=form_data)
        self.assertFalse(form.is_valid())

class AcademicYearFormTest(TestCase):
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

    def test_academic_year_form_valid(self):
        form_data = {
            'batch': self.batch.id,
            'start_year': 2023,
            'end_year': 2024
        }
        form = AcademicYearForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_academic_year_form_missing_required_fields(self):
        form_data = {
            'batch': self.batch.id
        }
        form = AcademicYearForm(data=form_data)
        self.assertFalse(form.is_valid())

class SemesterFormTest(TestCase):
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

    def test_semester_form_valid(self):
        form_data = {
            'academic_year': self.academic_year.id,
            'number': 1,
            'name': 'First Semester'
        }
        form = SemesterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_semester_form_missing_required_fields(self):
        form_data = {
            'academic_year': self.academic_year.id
        }
        form = SemesterForm(data=form_data)
        self.assertFalse(form.is_valid())

class CourseFormTest(TestCase):
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

    def test_course_form_valid(self):
        form_data = {
            'name': 'Introduction to Programming',
            'code': 'CS101',
            'credits': 4,
            'department': self.department.id,
            'semester': self.semester.id
        }
        form = CourseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_course_form_missing_required_fields(self):
        form_data = {
            'name': 'Introduction to Programming',
            'code': 'CS101'
        }
        form = CourseForm(data=form_data)
        self.assertFalse(form.is_valid())

class AssignTeacherFormTest(TestCase):
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

    def test_assign_teacher_form_valid(self):
        form_data = {
            'teacher': self.teacher.id,
            'course': self.course.id,
            'academic_year': self.academic_year.id
        }
        form = AssignTeacherForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_assign_teacher_form_missing_required_fields(self):
        form_data = {
            'teacher': self.teacher.id,
            'course': self.course.id
        }
        form = AssignTeacherForm(data=form_data)
        self.assertFalse(form.is_valid())

class EnrollStudentFormTest(TestCase):
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

    def test_enroll_student_form_valid(self):
        form_data = {
            'student': self.student.id,
            'course': self.course.id,
            'academic_year': self.academic_year.id
        }
        form = EnrollStudentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_enroll_student_form_missing_required_fields(self):
        form_data = {
            'student': self.student.id,
            'course': self.course.id
        }
        form = EnrollStudentForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_enroll_student_form_queryset_filter(self):
        """Test that student queryset is filtered to only include students"""
        # Create a teacher user
        teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )
        
        form = EnrollStudentForm()
        
        # Check that only students are in the queryset
        student_ids = list(form.fields['student'].queryset.values_list('id', flat=True))
        self.assertIn(self.student.id, student_ids)
        self.assertNotIn(teacher.id, student_ids)

class BulkEnrollStudentsFormTest(TestCase):
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

    def test_bulk_enroll_students_form_valid(self):
        form_data = {
            'batch': self.batch.id,
            'semester': self.semester.id,
            'students': [self.student.id],
            'courses': [self.course.id]
        }
        form = BulkEnrollStudentsForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_bulk_enroll_students_form_minimal_valid(self):
        # Students and courses are not required
        form_data = {
            'batch': self.batch.id,
            'semester': self.semester.id
        }
        form = BulkEnrollStudentsForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_bulk_enroll_students_form_widgets(self):
        """Test that the form uses the correct widgets"""
        form = BulkEnrollStudentsForm()
        
        # Check that the form uses the custom widgets
        self.assertIsInstance(form.fields['batch'].widget, SearchableSelect)
        self.assertIsInstance(form.fields['semester'].widget, SearchableSelect)
        self.assertIsInstance(form.fields['students'].widget, CustomCheckboxSelectMultiple)
        self.assertIsInstance(form.fields['courses'].widget, CustomCheckboxSelectMultiple)

class StudentUpdateFormTest(TestCase):
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

    def test_student_update_form_valid(self):
        form_data = {
            'username': 'updated_student',
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'updated@example.com',
            'student_id': 'S54321',
            'phone': '0987654321',
            'batch': self.batch.id
        }
        form = StudentUpdateForm(data=form_data, instance=self.student)
        self.assertTrue(form.is_valid())

    def test_student_update_form_initial_batch(self):
        form = StudentUpdateForm(instance=self.student)
        self.assertEqual(form.fields['batch'].initial, self.batch)
        
    def test_student_update_form_save_with_profile(self):
        """Test saving a student with an existing profile"""
        new_batch = Batch.objects.create(
            year='2024-2026',
            department=self.department,
            program=self.program
        )
        
        form_data = {
            'username': 'updated_student',
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'updated@example.com',
            'student_id': 'S54321',
            'phone': '0987654321',
            'batch': new_batch.id  # Change batch
        }
        
        form = StudentUpdateForm(data=form_data, instance=self.student)
        self.assertTrue(form.is_valid())
        
        # Save the form
        user = form.save()
        
        # Check that user was updated
        self.assertEqual(user.username, 'updated_student')
        
        # Check that profile was updated
        self.assertEqual(user.studentprofile.batch, new_batch)
        
    def test_student_update_form_save_without_profile(self):
        """Test saving a student without an existing profile"""
        # Create student without profile
        student_no_profile = User.objects.create_user(
            username='student2',
            password='password123',
            role='student'
        )
        
        form_data = {
            'username': 'updated_student2',
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'updated2@example.com',
            'student_id': 'S54322',
            'phone': '0987654322',
            'batch': self.batch.id
        }
        
        form = StudentUpdateForm(data=form_data, instance=student_no_profile)
        self.assertTrue(form.is_valid())
        
        # Save the form
        user = form.save()
        
        # Check that user was updated
        self.assertEqual(user.username, 'updated_student2')
        
        # Check that profile was created
        self.assertTrue(hasattr(user, 'studentprofile'))
        self.assertEqual(user.studentprofile.batch, self.batch)

class TeacherUpdateFormTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            password='password123',
            role='teacher'
        )

    def test_teacher_update_form_valid(self):
        form_data = {
            'username': 'updated_teacher',
            'first_name': 'Updated',
            'last_name': 'Teacher',
            'email': 'updated@example.com',
            'employee_id': 'T54321',
            'phone': '0987654321'
        }
        form = TeacherUpdateForm(data=form_data, instance=self.teacher)
        self.assertTrue(form.is_valid())

class TeacherCourseUpdateFormTest(TestCase):
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

    def test_teacher_course_update_form_valid(self):
        form_data = {
            'teacher': self.teacher.id,
            'course': self.course.id,
            'academic_year': self.academic_year.id
        }
        form = TeacherCourseUpdateForm(data=form_data, instance=self.teacher_course)
        self.assertTrue(form.is_valid())

    def test_teacher_course_update_form_queryset_filter(self):
        # Create a student user to test filtering
        student = User.objects.create_user(
            username='student1',
            password='password123',
            role='student'
        )
        
        form = TeacherCourseUpdateForm()
        # Should only include teachers, not students
        teacher_ids = list(form.fields['teacher'].queryset.values_list('id', flat=True))
        self.assertIn(self.teacher.id, teacher_ids)
        self.assertNotIn(student.id, teacher_ids)