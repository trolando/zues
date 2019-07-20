from django.conf.urls import include, url

from django.contrib import admin
admin.site.index_template = 'admin/zues_index.html'
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('zues.urls', namespace='zues')),
    url(r'^app/', include('appolo.urls')),
]
