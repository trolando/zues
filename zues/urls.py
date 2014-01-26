from django.conf.urls import patterns, url, include
from django.views.generic import DetailView, ListView
from zues import views

urlpatterns = patterns('moties.views',
    url(r'^$', views.view_home, name='home'),
    url(r'^loginverzonden/$', views.login_verzonden),
    url(r'^login/(?P<lid>\d+)/(?P<key>.+)/$', views.login, name='login'),
    url(r'^loguit/$', views.loguit, name='loguit'),
    url(r'^pm/nieuw/', views.NieuwePMPreview(), name='nieuwepm'),
    url(r'^pm/(?P<pk>\d+)/(?P<key>.+)/$', views.PMView.as_view(), name='pm'),
    url(r'^pm/wijzig/(?P<pk>\d+)/$', views.WijzigPM.as_view(), name='wijzigpm'),
    url(r'^pm/verwijder/(?P<pk>\d+)/$', views.VerwijderPM.as_view(), name='verwijderpm'),
)

