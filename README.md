# Student Attendance Management System (SAMS)

A comprehensive Django-based web application for managing student attendance in educational institutions. SAMS provides role-based access for administrators, teachers, and students to efficiently track and manage attendance records.

## Features

### For Administrators
- Dashboard with comprehensive statistics and analytics
- Manage departments, programs, batches, and courses
- Create and manage teacher and student accounts
- Assign teachers to courses
- Enroll students in courses (individually or in bulk)
- Generate attendance reports
- Search and filter functionality for all entities

### For Teachers
- Dashboard showing assigned courses
- Mark attendance for class sessions
- View attendance history for courses
- Track student attendance statistics

### For Students
- Dashboard showing enrolled courses
- View personal attendance records and statistics
- Track attendance percentage by course and semester

## Technologies Used

- **Backend**: Django 5.2.3
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, Bootstrap
- **Authentication**: Django's built-in authentication system with custom User model
- **Testing**: Django's testing framework with coverage analysis

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/durgeshgowdac/Student-Attendance-Management-System.git
   cd nirvana
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install django==5.2.3
   pip install coverage flake8  # For testing
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin account):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Usage

### Admin Workflow
1. Log in with admin credentials
2. Create departments, programs, and batches
3. Set up academic years and semesters
4. Create courses and assign them to departments/semesters
5. Create teacher and student accounts
6. Assign teachers to courses
7. Enroll students in courses
8. Generate and view attendance reports

### Teacher Workflow
1. Log in with teacher credentials
2. View assigned courses on the dashboard
3. Select a course to mark attendance
4. Create a new attendance session with date and time
5. Mark students as present, absent, or late
6. View attendance history for courses

### Student Workflow
1. Log in with student credentials
2. View enrolled courses on the dashboard
3. Check attendance statistics for each course
4. View detailed attendance records

## Project Structure

- **config/**: Django project configuration
  - settings.py: Project settings
  - urls.py: Main URL routing
  
- **sams/**: Main application
  - models.py: Database models
  - views.py: View functions
  - forms.py: Form definitions
  - widgets.py: Custom form widgets
  - urls.py: Application URL routing
  
- **templates/attendance/**: HTML templates
  - Base templates and layouts
  - Role-specific dashboards
  - CRUD operation templates
  
- **Test files**:
  - test_models.py: Tests for database models
  - test_forms.py: Tests for forms
  - test_views.py: Tests for views
  - test_integration.py: Integration tests
  - test_widgets.py: Tests for custom widgets

## Data Models

- **User**: Custom user model with role-based access (admin, teacher, student)
- **Department**: Academic departments
- **Program**: Academic programs (e.g., B.Tech, M.Tech)
- **Batch**: Student batches with year ranges
- **AcademicYear**: Academic years for batches
- **Semester**: Semesters within academic years
- **Course**: Courses with credits and department associations
- **TeacherCourse**: Assignments of teachers to courses
- **StudentCourse**: Enrollments of students in courses
- **AttendanceSession**: Class sessions for attendance tracking
- **Attendance**: Individual attendance records for students

## Testing

The project includes a comprehensive test suite covering models, forms, views, and integration tests.

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --models
python run_tests.py --forms
python run_tests.py --views
python run_tests.py --integration

# Run with coverage analysis
python run_tests.py --coverage
```

For more detailed testing information, refer to the TEST_README.md file.

## Security Considerations

- The project uses Django's built-in security features
- Role-based access control is implemented for all views
- Password validation is enforced for user accounts
- CSRF protection is enabled for all forms

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting changes
3. Follow Django's coding style and best practices
4. Update documentation for new features

## License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute this software in both personal and commercial projects, as long as you include the original license.

See the [LICENSE](LICENSE) file for full details.
