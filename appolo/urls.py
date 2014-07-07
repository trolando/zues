from django.conf.urls import patterns, url

from appolo import views

urlpatterns = patterns('',
    url(r'^data$', views.data, name='data'),
)
