from django.urls import include, re_path

from django.contrib import admin
admin.site.index_template = 'admin/zues_index.html'
admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'', include(('zues.urls', 'zues'), namespace='zues')),
    re_path(r'^app/', include('appolo.urls')),
]
