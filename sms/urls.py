from django.urls import path
from . import views

urlpatterns = [
    path('createsmsrequest', views.QueueSMSView.as_view()),
]
