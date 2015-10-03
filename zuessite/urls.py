from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.site.index_template = 'admin/zues_index.html'
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('zues.urls', namespace='zues')),
    url(r'^app/', include('appolo.urls')),
)
