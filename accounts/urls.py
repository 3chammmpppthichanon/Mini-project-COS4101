from django.urls import path
from . import views
from .views import SubmissionView, download_submission

urlpatterns = [
    path('', views.index, name='index'),
    path('sing_up/', views.sing_up, name='sing_up'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('project_list/', views.project_list, name='project_list'),
    path('advisor_list/', views.advisor_list, name='advisor_list'),
    path('completed_projects/', views.completed_project, name='completed_projects'),
    path('projects/<int:project_id>/submissions/', SubmissionView.as_view(), name='submissions'),
    path('submissions/<int:submission_id>/download/', download_submission, name='download_submission'),
    path('Manage/', views.manage_project, name='manage_project'),
    path('Time_sent/', views.time_sent, name='time_sent'),
    path('Create_project/', views.create_project, name='create_project'),
]
