from django.conf.urls import patterns, url, include
from django.views.generic import DetailView, ListView
from zues import views

urlpatterns = patterns('moties.views',
    url(r'^$', views.view_home, name='home'),
    url(r'^loginverzonden/$', views.login_verzonden),
    url(r'^login/(?P<lid>\d+)/(?P<key>.+)/$', views.login, name='login'),
    url(r'^loguit/$', views.loguit, name='loguit'),

    url(r'^pm/(?P<pk>\d+)/(?P<key>.+)/$', views.PMView.as_view(), name='pm'),
    url(r'^pm/nieuw/', views.NieuwePM.as_view(), name='nieuwepm'),
    url(r'^pm/wijzig/(?P<pk>\d+)/$', views.WijzigPM.as_view(), name='wijzigpm'),
    url(r'^pm/verwijder/(?P<pk>\d+)/$', views.VerwijderPM.as_view(), name='verwijderpm'),

    url(r'^apm/(?P<pk>\d+)/(?P<key>.+)/$', views.APMView.as_view(), name='apm'),
    url(r'^apm/nieuw/', views.NieuweAPM.as_view(), name='nieuweapm'),
    url(r'^apm/wijzig/(?P<pk>\d+)/$', views.WijzigAPM.as_view(), name='wijzigapm'),
    url(r'^apm/verwijder/(?P<pk>\d+)/$', views.VerwijderAPM.as_view(), name='verwijderapm'),

    url(r'^org/(?P<pk>\d+)/(?P<key>.+)/$', views.ORGView.as_view(), name='org'),
    url(r'^org/nieuw/', views.NieuweORG.as_view(), name='nieuweorg'),
    url(r'^org/wijzig/(?P<pk>\d+)/$', views.WijzigORG.as_view(), name='wijzigorg'),
    url(r'^org/verwijder/(?P<pk>\d+)/$', views.VerwijderORG.as_view(), name='verwijderorg'),
)

