from django.urls import re_path
from zues import views


urlpatterns = [
    re_path(r'^$', views.view_home, name='home'),
    re_path(r'^loginverzonden/$', views.login_verzonden),
    re_path(r'^login/(?P<lid>\d+)/(?P<key>.+)/$', views.login, name='login'),
    re_path(r'^loguit/$', views.loguit, name='loguit'),

    re_path(r'^pm/(?P<pk>\d+)/(?P<key>.+)/$', views.PMView.as_view(), name='pm'),
    re_path(r'^pm/nieuw/', views.NieuwePM.as_view(), name='nieuwepm'),
    re_path(r'^pm/wijzig/(?P<pk>\d+)/$', views.WijzigPM.as_view(), name='wijzigpm'),
    re_path(r'^pm/verwijder/(?P<pk>\d+)/$', views.VerwijderPM.as_view(), name='verwijderpm'),

    re_path(r'^apm/(?P<pk>\d+)/(?P<key>.+)/$', views.APMView.as_view(), name='apm'),
    re_path(r'^apm/nieuw/', views.NieuweAPM.as_view(), name='nieuweapm'),
    re_path(r'^apm/wijzig/(?P<pk>\d+)/$', views.WijzigAPM.as_view(), name='wijzigapm'),
    re_path(r'^apm/verwijder/(?P<pk>\d+)/$', views.VerwijderAPM.as_view(), name='verwijderapm'),

    re_path(r'^org/(?P<pk>\d+)/(?P<key>.+)/$', views.ORGView.as_view(), name='org'),
    re_path(r'^org/nieuw/', views.NieuweORG.as_view(), name='nieuweorg'),
    re_path(r'^org/wijzig/(?P<pk>\d+)/$', views.WijzigORG.as_view(), name='wijzigorg'),
    re_path(r'^org/verwijder/(?P<pk>\d+)/$', views.VerwijderORG.as_view(), name='verwijderorg'),

    re_path(r'^res/(?P<pk>\d+)/(?P<key>.+)/$', views.RESView.as_view(), name='res'),
    re_path(r'^res/nieuw/', views.NieuweRES.as_view(), name='nieuweres'),
    re_path(r'^res/wijzig/(?P<pk>\d+)/$', views.WijzigRES.as_view(), name='wijzigres'),
    re_path(r'^res/verwijder/(?P<pk>\d+)/$', views.VerwijderRES.as_view(), name='verwijderres'),

    re_path(r'^am/(?P<pk>\d+)/(?P<key>.+)/$', views.AMView.as_view(), name='am'),
    re_path(r'^am/nieuw/', views.NieuweAM.as_view(), name='nieuweam'),
    re_path(r'^am/wijzig/(?P<pk>\d+)/$', views.WijzigAM.as_view(), name='wijzigam'),
    re_path(r'^am/verwijder/(?P<pk>\d+)/$', views.VerwijderAM.as_view(), name='verwijderam'),

    re_path(r'^hr/(?P<pk>\d+)/(?P<key>.+)/$', views.HRView.as_view(), name='hr'),
    re_path(r'^hr/nieuw/', views.NieuweHR.as_view(), name='nieuwehr'),
    re_path(r'^hr/wijzig/(?P<pk>\d+)/$', views.WijzigHR.as_view(), name='wijzighr'),
    re_path(r'^hr/verwijder/(?P<pk>\d+)/$', views.VerwijderHR.as_view(), name='verwijderhr'),

    re_path(r'^alles/$', views.view_publiek),
    re_path(r'^handig/voor/arend/$', views.view_publiek, name='publiek'),
    re_path(r'^export/$', views.view_export, name='export'),
    re_path(r'^exportsnc/$', views.view_export_snc, name='exportsnc'),
    re_path(r'^reorder/$', views.view_reorder, name='reorder'),

    re_path(r'^lidnummer/$', views.view_lidnummer, name='lidnummer'),
    re_path(r'^lidnummerverzonden/$', views.lidnummer_verzonden),
]
