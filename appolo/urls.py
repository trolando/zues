from django.conf.urls import url

from appolo import views

urlpatterns = [
    url(r'^data$', views.data, name='data'),
]
