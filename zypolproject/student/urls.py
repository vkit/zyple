from django.conf.urls import url, include

from student import views

urlpatterns = [
    url(r'^register/$', views.Register.as_view()),
    url(r'^login/$', views.Login.as_view()),
    url(r'^task/$', views.CreateTask.as_view()),
    url(r'update_profile/$', views.UpdateProfile.as_view()),
    url(r'^delete_task/(?P<task_id>[0-9]+)/$', views.CreateTask.as_view(),name='delete_task'),
    url(r'^task_list/$', views.TaskList.as_view()),

    url(r'^assign/$', views.AssignTask.as_view()),
    url(r'^student_update/$', views.StudentUpdateStatus.as_view()),
    url(r'^approve/$', views.ApproveView.as_view()),




]