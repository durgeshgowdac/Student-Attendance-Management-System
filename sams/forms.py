from django import forms
from .models import *
from .widgets import *
from django.db import IntegrityError

class DeduplicationMixin:
    def save(self, commit=True):
        try:
            return super().save(commit=commit)
        except IntegrityError:
            self.add_error(None, "Duplicate entry already exists.")
            raise

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.PasswordInput, forms.EmailInput, forms.NumberInput, forms.Select, forms.SelectMultiple)):
                css_class = 'form-control' if not isinstance(widget, forms.SelectMultiple) else 'form-select'
                existing_classes = widget.attrs.get('class', '')
                widget.attrs['class'] = f'{existing_classes} {css_class}'.strip()


class StudentCreationForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), widget=forms.Select())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'student_id', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'student'
        if commit:
            user.save()
            StudentProfile.objects.create(user=user, batch=self.cleaned_data['batch'])
        return user


class TeacherCreationForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'phone']

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role = 'teacher'
        if commit:
            user.save()
        return user


class AssignTeacherForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = TeacherCourse
        fields = ['teacher', 'course', 'academic_year']


class BulkEnrollStudentsForm(BootstrapFormMixin, forms.Form):
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(), 
        label="Select Batch",
        widget=SearchableSelect()
    )
    semester = forms.ModelChoiceField(
        queryset=Semester.objects.all(), 
        label="Select Semester",
        widget=SearchableSelect()
    )
    
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student'), 
        widget=CustomCheckboxSelectMultiple(),
        required=False,
        label="Select Students"
    )
    courses = forms.ModelMultipleChoiceField(
        queryset=Course.objects.all(),
        widget=CustomCheckboxSelectMultiple(),
        required=False,
        label="Select Courses"
    )


class DepartmentForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code']


class CourseForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'credits', 'department', 'semester']


class BatchForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['year', 'department', 'program']


class ProgramForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'code']


class AcademicYearForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['batch', 'start_year', 'end_year']


class SemesterForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = Semester
        fields = ['academic_year', 'number', 'name']


class StudentUpdateForm(BootstrapFormMixin, forms.ModelForm):
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), widget=forms.Select())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'student_id', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'studentprofile'):
            self.fields['batch'].initial = self.instance.studentprofile.batch

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Update batch
            if hasattr(user, 'studentprofile'):
                user.studentprofile.batch = self.cleaned_data['batch']
                user.studentprofile.save()
            else:
                StudentProfile.objects.create(user=user, batch=self.cleaned_data['batch'])
        return user


class TeacherUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'phone']


class EnrollStudentForm(BootstrapFormMixin, DeduplicationMixin, forms.ModelForm):
    class Meta:
        model = StudentCourse
        fields = ['student', 'course', 'academic_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(role='student')


class TeacherCourseUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = TeacherCourse
        fields = ['teacher', 'course', 'academic_year']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')






