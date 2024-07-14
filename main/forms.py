from django import forms
from .models import Student, Grade, Teacher, Homework, Activity, Communication

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'parent']

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['subject', 'grade', 'comments']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['bio']

class HomeworkForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Homework
        fields = ['student', 'subject', 'description', 'due_date']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['description', 'date']

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['student', 'message']
