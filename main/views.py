from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.template.loader import render_to_string
from django.http import HttpResponse
from .forms import StudentForm, GradeForm, TeacherForm, HomeworkForm, ActivityForm, CommunicationForm
from .models import Student, Grade, Homework, Activity, Communication, Teacher, Parent
from .tasks import send_email_task
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms 
from django.contrib.auth import logout as django_logout
from django.urls import reverse
import pdfkit
from datetime import date


def home(request):
    return render(request, 'main/home.html')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user_type = request.POST.get('user_type')
            if user_type == 'teacher':
                Teacher.objects.create(user=user)
            elif user_type == 'parent':
                Parent.objects.create(user=user)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    # user type selection field to the form
    form.fields['user_type'] = forms.ChoiceField(choices=(('teacher', 'Teacher'), ('parent', 'Parent')), widget=forms.RadioSelect)

    return render(request, 'registration/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def dashboard(request):
    if hasattr(request.user, 'teacher'):
        teacher = request.user.teacher
        students = Student.objects.filter(teacher=teacher)
        homeworks = Homework.objects.filter(student__in=students)
        activities = Activity.objects.filter(student__in=students)
        communications = Communication.objects.filter(student__in=students)
        
        if request.method == 'POST':
            homework_form = HomeworkForm(request.POST)
            activity_form = ActivityForm(request.POST)
            communication_form = CommunicationForm(request.POST)
            
            if homework_form.is_valid():
                homework_form.save()
                return redirect('dashboard')
            if activity_form.is_valid():
                activity_form.save()
                return redirect('dashboard')
            if communication_form.is_valid():
                communication = communication_form.save(commit=False)
                communication.teacher = teacher
                communication.save()
                return redirect('dashboard')
        else:
            homework_form = HomeworkForm()
            activity_form = ActivityForm()
            communication_form = CommunicationForm()
            
        context = {
            'students': students,
            'homeworks': homeworks,
            'activities': activities,
            'communications': communications,
            'homework_form': homework_form,
            'activity_form': activity_form,
            'communication_form': communication_form,
        }
        return render(request, 'main/teacher_dashboard.html', context)
    elif hasattr(request.user, 'parent'):
        parent = request.user.parent
        children = parent.children.all()
        homeworks = Homework.objects.filter(student__in=children)
        activities = Activity.objects.filter(student__in=children)
        communications = Communication.objects.filter(student__in=children)
        
        context = {
            'children': children,
            'homeworks': homeworks,
            'activities': activities,
            'communications': communications,
        }
        return render(request, 'main/parent_dashboard.html', context)
    return redirect('home')

@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            student.teacher.add(request.user.teacher)
            return redirect('dashboard')
    else:
        form = StudentForm()
    return render(request, 'main/add_student.html', {'form': form})


@login_required
def add_grade(request, student_id):
    student = Student.objects.get(id=student_id)
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.student = student
            grade.save()
            return redirect('dashboard')
    else:
        form = GradeForm()
    return render(request, 'main/add_grade.html', {'form': form, 'student': student})


@login_required
def update_profile(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        teacher = None

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            if teacher is None:
                # If teacher instance does not exist, create it
                teacher = Teacher.objects.create(user=request.user)
            form.instance = teacher  # Set instance of the form to the retrieved or created teacher object
            form.save()
            return redirect('dashboard')
    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'main/update_profile.html', {'form': form})


@login_required
def generate_report(request, student_id):
    report_date = date.today()
    student = Student.objects.get(id=student_id)
    grades = Grade.objects.filter(student=student)
    report_html = render_to_string('main/report_template.html', {'student': student, 'grades': grades, 'report_date': date.today()})

    pdf = pdfkit.from_string(report_html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{student_id}.pdf"'
    send_email_task.delay(student.parent.user.email, 'Student Report', 'Please find the attached report.', pdf)
    return response


@login_required
def view_child_profile(request, child_id):
    child = Student.objects.get(id=child_id)
    grades = Grade.objects.filter(student=child)
    homework = Homework.objects.filter(student=child)
    activities = Activity.objects.filter(student=child)
    communications = Communication.objects.filter(student=child)
    return render(request, 'main/child_profile.html', {
        'child': child,
        'grades': grades,
        'homework': homework,
        'activities': activities,
        'communications': communications,
    })

@login_required
def view_communication(request, communication_id):
    communication = get_object_or_404(Communication, id=communication_id)
    return render(request, 'main/view_communication.html', {'communication': communication})

@login_required
def view_homework(request, homework_id):
    homework = get_object_or_404(Homework, id=homework_id)
    
     # Define context dictionary to pass data to template
    context = {
        'homework': homework,
    }
    
    return render(request, 'main/view_homework.html', context)

def logout(request):
    django_logout(request)
    return redirect('login')  # Redirect to the login after logout
