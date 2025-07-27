# SAMS Test Suite Documentation

This document explains how to run and understand the comprehensive test suite for the Student Attendance Management System (SAMS).

## Test Files Overview

### 1. `test_models.py`
Tests all Django models including:
- User model with different roles (admin, teacher, student)
- Department, Program, Batch models
- Academic Year and Semester models
- Course model
- Student and Teacher profiles
- Attendance Session and Attendance models
- Model relationships and constraints
- Unique constraint validations

### 2. `test_forms.py`
Tests all Django forms including:
- Student and Teacher creation forms
- Department, Program, Batch creation forms
- Course creation forms
- Assignment and enrollment forms
- Form validation and error handling
- Password matching validation
- Required field validation

### 3. `test_views.py`
Tests all Django views including:
- Authentication and login requirements
- Role-based access control
- Admin dashboard and management views
- Teacher course management and attendance marking
- Student attendance viewing
- AJAX endpoints for dynamic data
- Search and filter functionality
- Bulk operations

### 4. `test_integration.py`
Integration tests including:
- Complete attendance workflow (admin setup → teacher marking → student viewing)
- Bulk enrollment operations
- Data integrity and constraint enforcement
- Role-based permission testing across the system
- Attendance percentage calculations
- Search and filter functionality

### 5. `sams/tests.py`
Basic SAMS app tests including:
- User creation and authentication
- Model relationships
- Basic attendance flow

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Make the script executable (Linux/Mac)
chmod +x run_tests.py
./run_tests.py
```

### Specific Test Categories
```bash
# Run only model tests
python run_tests.py --models

# Run only form tests
python run_tests.py --forms

# Run only view tests
python run_tests.py --views

# Run only integration tests
python run_tests.py --integration

# Run coverage analysis
python run_tests.py --coverage

# Run code linting
python run_tests.py --lint

# Run security checks
python run_tests.py --security

# Check for pending migrations
python run_tests.py --migrations
```

### Manual Django Test Commands
```bash
# Run specific test file
python manage.py test test_models -v 2

# Run specific test class
python manage.py test test_models.UserModelTest -v 2

# Run specific test method
python manage.py test test_models.UserModelTest.test_user_creation -v 2

# Run all tests with verbose output
python manage.py test -v 2

# Run tests with coverage
coverage run --source=Student Attendance Management System manage.py test
coverage report -m
coverage html
```

## Test Structure

### Model Tests
- **User Model**: Role validation, unique constraints, authentication
- **Department Model**: Creation, string representation, unique codes
- **Program Model**: Creation, validation, constraints
- **Batch Model**: Relationships with department/program, unique together constraints
- **Academic Year Model**: Batch relationships, year validation
- **Semester Model**: Academic year relationships, number validation
- **Course Model**: Department/semester relationships, credit validation
- **Profile Models**: Student/Teacher profile creation and relationships
- **Assignment Models**: Teacher-course and student-course assignments
- **Attendance Models**: Session creation, attendance marking, status validation

### Form Tests
- **Creation Forms**: Student/Teacher creation with password validation
- **Management Forms**: Department, Program, Batch, Course creation
- **Assignment Forms**: Teacher-course assignment, student enrollment
- **Update Forms**: Student/Teacher profile updates
- **Bulk Forms**: Bulk student enrollment
- **Validation**: Required fields, password matching, unique constraints

### View Tests
- **Authentication**: Login requirements, role-based access
- **Admin Views**: Dashboard, creation forms, management interfaces
- **Teacher Views**: Course management, attendance marking, history
- **Student Views**: Dashboard, attendance viewing
- **AJAX Views**: Dynamic data loading, search functionality
- **Permissions**: Role-based access control testing

### Integration Tests
- **Complete Workflows**: End-to-end attendance management process
- **Bulk Operations**: Mass enrollment and assignment operations
- **Data Integrity**: Constraint enforcement, transaction handling
- **Permission Integration**: Cross-system role validation
- **Calculation Tests**: Attendance percentage accuracy
- **Search/Filter**: Dynamic filtering and search functionality

## Test Data Setup

Each test class includes a `setUp()` method that creates the necessary test data:

```python
def setUp(self):
    # Create users with different roles
    self.admin = User.objects.create_user(...)
    self.teacher = User.objects.create_user(...)
    self.student = User.objects.create_user(...)
    
    # Create academic structure
    self.department = Department.objects.create(...)
    self.program = Program.objects.create(...)
    self.batch = Batch.objects.create(...)
    # ... etc
```

## Expected Test Results

When all tests pass, you should see output similar to:
```
TEST SUMMARY
================================================================================
Total Duration: 45.23 seconds
Tests Run: 5
Passed: 5
Failed: 0

DETAILED RESULTS:
  ✅ PASSED - Model Tests
  ✅ PASSED - Form Tests
  ✅ PASSED - View Tests
  ✅ PASSED - Integration Tests
  ✅ PASSED - SAMS App Tests

🎉 All tests passed! 🎉
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure Django settings are configured
   export DJANGO_SETTINGS_MODULE=config.settings
   ```

2. **Database Issues**
   ```bash
   # Run migrations before testing
   python manage.py migrate
   ```

3. **Missing Dependencies**
   ```bash
   # Install test dependencies
   pip install coverage flake8
   ```

4. **Permission Errors**
   ```bash
   # Make test runner executable
   chmod +x run_tests.py
   ```

### Test Database

Django automatically creates a test database for running tests. This database is:
- Created before tests run
- Destroyed after tests complete
- Isolated from your development database
- Named with `test_` prefix

## Coverage Analysis

The test suite includes coverage analysis to show which parts of your code are tested:

```bash
# Generate coverage report
python run_tests.py --coverage

# View HTML coverage report
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

These tests are designed to work with CI/CD systems. Example GitHub Actions workflow:

```yaml
name: Django Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: python run_tests.py
```

## Best Practices

1. **Run tests frequently** during development
2. **Write tests first** for new features (TDD)
3. **Keep tests isolated** - each test should be independent
4. **Use descriptive test names** that explain what is being tested
5. **Test edge cases** and error conditions
6. **Maintain high test coverage** (aim for >90%)
7. **Update tests** when changing functionality

## Contributing

When adding new features to SAMS:

1. Write tests for new models, forms, and views
2. Update integration tests for new workflows
3. Ensure all tests pass before submitting changes
4. Add test documentation for complex scenarios

## Support

If you encounter issues with the test suite:

1. Check the troubleshooting section above
2. Verify your Django setup and dependencies
3. Review test output for specific error messages
4. Ensure database migrations are up to date