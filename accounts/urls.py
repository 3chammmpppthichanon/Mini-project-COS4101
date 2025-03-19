from django.urls import path
from . import views
from .views import SubmissionView, download_submission

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('projects/<int:project_id>/submissions/', SubmissionView.as_view(), name='submissions'),
    path('submissions/<int:submission_id>/download/', download_submission, name='download_submission'),
]
