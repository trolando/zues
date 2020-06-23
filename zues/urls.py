from django.conf.urls import url
from zues import views


urlpatterns = [
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

    url(r'^res/(?P<pk>\d+)/(?P<key>.+)/$', views.RESView.as_view(), name='res'),
    url(r'^res/nieuw/', views.NieuweRES.as_view(), name='nieuweres'),
    url(r'^res/wijzig/(?P<pk>\d+)/$', views.WijzigRES.as_view(), name='wijzigres'),
    url(r'^res/verwijder/(?P<pk>\d+)/$', views.VerwijderRES.as_view(), name='verwijderres'),

    url(r'^am/(?P<pk>\d+)/(?P<key>.+)/$', views.AMView.as_view(), name='am'),
    url(r'^am/nieuw/', views.NieuweAM.as_view(), name='nieuweam'),
    url(r'^am/wijzig/(?P<pk>\d+)/$', views.WijzigAM.as_view(), name='wijzigam'),
    url(r'^am/verwijder/(?P<pk>\d+)/$', views.VerwijderAM.as_view(), name='verwijderam'),

    url(r'^hr/(?P<pk>\d+)/(?P<key>.+)/$', views.HRView.as_view(), name='hr'),
    url(r'^hr/nieuw/', views.NieuweHR.as_view(), name='nieuwehr'),
    url(r'^hr/wijzig/(?P<pk>\d+)/$', views.WijzigHR.as_view(), name='wijzighr'),
    url(r'^hr/verwijder/(?P<pk>\d+)/$', views.VerwijderHR.as_view(), name='verwijderhr'),

    url(r'^alles/$', views.view_publiek),
    url(r'^handig/voor/arend/$', views.view_publiek, name='publiek'),
    url(r'^export/$', views.view_export, name='export'),
    url(r'^exportsnc/$', views.view_export_snc, name='exportsnc'),
    url(r'^reorder/$', views.view_reorder, name='reorder'),

    url(r'^lidnummer/$', views.view_lidnummer, name='lidnummer'),
    url(r'^lidnummerverzonden/$', views.lidnummer_verzonden),
]
