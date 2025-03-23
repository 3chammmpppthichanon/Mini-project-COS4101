from django.urls import path
from . import views
from .views import SubmissionView, download_submission

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('project_list/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/submissions/', SubmissionView.as_view(), name='submissions'),
    path('submissions/<int:submission_id>/download/', download_submission, name='download_submission'),
]
