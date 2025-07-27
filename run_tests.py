#!/usr/bin/env python
"""
Comprehensive Test Runner for SAMS (sams)

This script runs all test suites and provides detailed reporting.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.core.management import execute_from_command_line
import subprocess
import time
from datetime import datetime

def setup_django():
    """Setup Django environment for testing"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

def run_command(command, description):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Duration: {duration:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
            
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return False, "", str(e)

def run_specific_tests():
    """Run specific test categories"""
    test_commands = [
        {
            'command': 'python manage.py test test_models -v 2',
            'description': 'Model Tests',
            'file': 'test_models.py'
        },
        {
            'command': 'python manage.py test test_forms -v 2',
            'description': 'Form Tests',
            'file': 'test_forms.py'
        },
        {
            'command': 'python manage.py test test_views -v 2',
            'description': 'View Tests',
            'file': 'test_views.py'
        },
        {
            'command': 'python manage.py test test_views_extended -v 2',
            'description': 'Extended View Tests',
            'file': 'test_views_extended.py'
        },
        {
            'command': 'python manage.py test test_widgets -v 2',
            'description': 'Widget Tests',
            'file': 'test_widgets.py'
        },
        {
            'command': 'python manage.py test test_integration -v 2',
            'description': 'Integration Tests',
            'file': 'test_integration.py'
        },
        {
            'command': 'python manage.py test sams.tests -v 2',
            'description': 'SAMS App Tests',
            'file': 'sams/tests.py'
        }
    ]
    
    results = []
    total_start_time = time.time()
    
    print(f"Starting SAMS Test Suite at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for test_config in test_commands:
        # Check if test file exists
        if not os.path.exists(test_config['file']):
            print(f"\nSkipping {test_config['description']} - File {test_config['file']} not found")
            continue
            
        success, stdout, stderr = run_command(
            test_config['command'], 
            test_config['description']
        )
        
        results.append({
            'description': test_config['description'],
            'success': success,
            'stdout': stdout,
            'stderr': stderr
        })
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Tests Run: {len(results)}")
    
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed > 0:
        print(f"\nFAILED TESTS:")
        for result in results:
            if not result['success']:
                print(f"  - {result['description']}")
    
    print(f"\nDETAILED RESULTS:")
    for result in results:
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        print(f"  {status} - {result['description']}")
    
    return failed == 0

def run_coverage_analysis():
    """Run test coverage analysis"""
    print(f"\n{'='*60}")
    print("Running Coverage Analysis")
    print(f"{'='*60}")
    
    # Install coverage if not available
    try:
        import coverage
    except ImportError:
        print("Installing coverage package...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'coverage'], check=True)
    
    # Run coverage
    commands = [
        'coverage erase',
        'coverage run --source=sams manage.py test test_models test_forms test_views test_integration sams.tests',
        'coverage report -m',
        'coverage html'
    ]
    
    for cmd in commands:
        success, stdout, stderr = run_command(cmd, f"Coverage: {cmd}")
        if not success and 'coverage run' in cmd:
            print("Coverage analysis failed, but continuing...")

def run_linting():
    """Run code quality checks"""
    print(f"\n{'='*60}")
    print("Running Code Quality Checks")
    print(f"{'='*60}")
    
    # Check if flake8 is available
    try:
        subprocess.run(['flake8', '--version'], capture_output=True, check=True)
        flake8_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        flake8_available = False
    
    if flake8_available:
        run_command('flake8 sams/ --max-line-length=120 --exclude=migrations', 'Flake8 Linting')
    else:
        print("Flake8 not available, skipping linting")

def check_migrations():
    """Check for pending migrations"""
    print(f"\n{'='*60}")
    print("Checking Migrations")
    print(f"{'='*60}")
    
    run_command('python manage.py makemigrations --dry-run --check', 'Check for pending migrations')

def run_security_checks():
    """Run Django security checks"""
    print(f"\n{'='*60}")
    print("Running Security Checks")
    print(f"{'='*60}")
    
    run_command('python manage.py check --deploy', 'Django Security Check')

def main():
    """Main test runner function"""
    print("SAMS Test Suite Runner")
    print("=" * 80)
    
    # Setup Django
    setup_django()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--models':
            run_command('python manage.py test test_models -v 2', 'Model Tests Only')
        elif sys.argv[1] == '--forms':
            run_command('python manage.py test test_forms -v 2', 'Form Tests Only')
        elif sys.argv[1] == '--views':
            run_command('python manage.py test test_views -v 2', 'View Tests Only')
        elif sys.argv[1] == '--integration':
            run_command('python manage.py test test_integration -v 2', 'Integration Tests Only')
        elif sys.argv[1] == '--coverage':
            run_coverage_analysis()
        elif sys.argv[1] == '--lint':
            run_linting()
        elif sys.argv[1] == '--security':
            run_security_checks()
        elif sys.argv[1] == '--migrations':
            check_migrations()
        elif sys.argv[1] == '--help':
            print_help()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print_help()
    else:
        # Run all tests
        success = run_specific_tests()
        
        # Run additional checks
        check_migrations()
        run_security_checks()
        run_linting()
        run_coverage_analysis()
        
        if success:
            print(f"\n🎉 All tests passed! 🎉")
            sys.exit(0)
        else:
            print(f"\n💥 Some tests failed! 💥")
            sys.exit(1)

def print_help():
    """Print help information"""
    help_text = """
SAMS Test Suite Runner

Usage: python run_tests.py [option]

Options:
  --models      Run model tests only
  --forms       Run form tests only  
  --views       Run view tests only
  --integration Run integration tests only
  --coverage    Run coverage analysis only
  --lint        Run code linting only
  --security    Run security checks only
  --migrations  Check for pending migrations only
  --help        Show this help message

No option: Run all tests and checks
"""
    print(help_text)

if __name__ == '__main__':
    main()