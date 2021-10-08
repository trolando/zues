from django.urls import re_path

from appolo import views

urlpatterns = [
    re_path(r'^data$', views.data, name='data'),
]
