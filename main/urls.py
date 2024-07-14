from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add_student/', views.add_student, name='add_student'),
    path('add_grade/<int:student_id>/', views.add_grade, name='add_grade'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('generate_report/<int:student_id>/', views.generate_report, name='generate_report'),
    path('view_child_profile/<int:child_id>/', views.view_child_profile, name='view_child_profile'),
    path('view_communication/<int:communication_id>/', views.view_communication, name='view_communication'),
    path('homework/<int:homework_id>/', views.view_homework, name='view_homework'),
]
