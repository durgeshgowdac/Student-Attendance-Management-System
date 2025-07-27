from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from sams.models import *
import json

User = get_user_model()

class StudentUpdateFormViewTest(TestCase):
    """Test the StudentUpdateForm in a view context"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
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
        self.batch1 = Batch.objects.create(
            year='2023-2025',
            department=self.department,
            program=self.program
        )
        self.batch2 = Batch.objects.create(
            year='2024-2026',
            department=self.department,
            program=self.program
        )
        
        # Create student with profile
        self.student = User.objects.create_user(
            username='student1',
            password='student123',
            role='student',
            first_name='John',
            last_name='Doe',
            student_id='S001'
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student,
            batch=self.batch1
        )
        
        # Create student without profile
        self.student_no_profile = User.objects.create_user(
            username='student2',
            password='student123',
            role='student',
            first_name='Jane',
            last_name='Smith',
            student_id='S002'
        )
        
        # Login as admin
        self.client.login(username='admin', password='admin123')
    
    def test_student_update_with_existing_profile(self):
        """Test updating a student with an existing profile"""
        # Mock the student_list view with update functionality
        url = reverse('student_list')
        
        # Simulate form submission with update_id
        response = self.client.post(url, {
            'update_id': self.student.id,
            'username': 'updated_student',
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'updated@example.com',
            'student_id': 'S001-updated',
            'phone': '9876543210',
            'batch': self.batch2.id  # Change batch
        })
        
        # Refresh student from database
        self.student.refresh_from_db()
        self.student.studentprofile.refresh_from_db()
        
        # Check that student was updated
        self.assertEqual(self.student.username, 'updated_student')
        self.assertEqual(self.student.first_name, 'Updated')
        self.assertEqual(self.student.student_id, 'S001-updated')
        
        # Check that profile was updated
        self.assertEqual(self.student.studentprofile.batch, self.batch2)
    
    def test_student_update_without_profile(self):
        """Test updating a student without an existing profile"""
        # Mock the student_list view with update functionality
        url = reverse('student_list')
        
        # Simulate form submission with update_id
        response = self.client.post(url, {
            'update_id': self.student_no_profile.id,
            'username': 'updated_student2',
            'first_name': 'Updated',
            'last_name': 'Student',
            'email': 'updated2@example.com',
            'student_id': 'S002-updated',
            'phone': '9876543210',
            'batch': self.batch2.id
        })
        
        # Refresh student from database
        self.student_no_profile.refresh_from_db()
        
        # Check that student was updated
        self.assertEqual(self.student_no_profile.username, 'updated_student2')
        self.assertEqual(self.student_no_profile.first_name, 'Updated')
        self.assertEqual(self.student_no_profile.student_id, 'S002-updated')
        
        # Check that profile was created
        self.assertTrue(hasattr(self.student_no_profile, 'studentprofile'))
        self.assertEqual(self.student_no_profile.studentprofile.batch, self.batch2)

class DeduplicationMixinViewTest(TestCase):
    """Test the DeduplicationMixin in a view context"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        # Create initial department
        self.department = Department.objects.create(
            name='Computer Science',
            code='CS'
        )
        
        # Login as admin
        self.client.login(username='admin', password='admin123')
    
    def test_deduplication_mixin_in_view(self):
        """Test that DeduplicationMixin works in a view context"""
        # Try to create a department with duplicate code
        url = reverse('create_department')
        
        response = self.client.post(url, {
            'name': 'Computer Engineering',
            'code': 'CS'  # Duplicate code
        })
        
        # Should stay on the same page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Duplicate entry already exists')
        
        # Check that no new department was created
        self.assertEqual(Department.objects.count(), 1)
    
    def test_deduplication_mixin_success_in_view(self):
        """Test that DeduplicationMixin allows valid entries"""
        # Create a department with unique code
        url = reverse('create_department')
        
        response = self.client.post(url, {
            'name': 'Mathematics',
            'code': 'MATH'  # Unique code
        })
        
        # Should redirect after success
        self.assertEqual(response.status_code, 302)
        
        # Check that new department was created
        self.assertEqual(Department.objects.count(), 2)
        self.assertTrue(Department.objects.filter(code='MATH').exists())

class BootstrapFormMixinViewTest(TestCase):
    """Test the BootstrapFormMixin in a view context"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        
        # Login as admin
        self.client.login(username='admin', password='admin123')
    
    def test_bootstrap_form_mixin_in_view(self):
        """Test that BootstrapFormMixin applies styles in a view context"""
        # Get the create department form
        url = reverse('create_department')
        
        response = self.client.get(url)
        
        # Check that form has Bootstrap classes
        self.assertContains(response, 'form-control')
        
        # Get the create student form
        url = reverse('create_student')
        
        response = self.client.get(url)
        
        # Check that form has Bootstrap classes
        self.assertContains(response, 'form-control')
        self.assertContains(response, 'form-select')

class WidgetViewTest(TestCase):
    """Test custom widgets in a view context"""
    
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
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
        
        # Create students
        for i in range(3):
            User.objects.create_user(
                username=f'student{i+1}',
                password='student123',
                role='student',
                student_id=f'S00{i+1}'
            )
        
        # Login as admin
        self.client.login(username='admin', password='admin123')
    
    def test_custom_checkbox_select_multiple_in_view(self):
        """Test that CustomCheckboxSelectMultiple renders correctly in a view"""
        # Get the bulk enroll form
        url = reverse('bulk_enroll_students')
        
        response = self.client.get(url)
        
        # Check that the widget renders correctly
        self.assertContains(response, 'checkbox-group')
        self.assertContains(response, 'form-check')
        self.assertContains(response, 'form-check-input')
        self.assertContains(response, 'form-check-label')
    
    def test_searchable_select_in_view(self):
        """Test that SearchableSelect renders correctly in a view"""
        # Get the bulk enroll form
        url = reverse('bulk_enroll_students')
        
        response = self.client.get(url)
        
        # Check that the widget renders correctly
        self.assertContains(response, 'searchable-select')
        self.assertContains(response, 'form-select')