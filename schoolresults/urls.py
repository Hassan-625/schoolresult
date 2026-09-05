from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
urlpatterns=[
 path("",views.home,name="home"), path("health/",views.health,name="health"), path("dashboard/",views.dashboard,name="dashboard"),
 path("login/",auth_views.LoginView.as_view(template_name="schoolresults/login.html"),name="login"), path("logout/",auth_views.LogoutView.as_view(),name="logout"),
 path("students/",views.student_list,name="student_list"), path("students/dashboard/",views.student_dashboard,name="student_dashboard"),
 path("students/<int:pk>/",views.student_detail,name="student_detail"), path("students/<int:pk>/download/",views.download_student_report,name="download_student_report"),
 path("results/",views.result_list,name="result_list"), path("results/add/",views.add_result,name="add_result"), path("results/enter/",views.add_result,name="enter_result"),
 path("classes/<str:class_level>/",views.class_results,name="class_results"), path("classes/<str:class_level>/compile/",views.trigger_compilation,name="trigger_compilation"),
 path("compiled/",views.compiled_results,name="compiled_results"),
]
