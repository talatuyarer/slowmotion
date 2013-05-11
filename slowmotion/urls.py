from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'action.views.index', name='index'),
    url(r'^get_users/', 'action.views.get_users', name='get_users'),
    url(r'^recording/', 'action.views.recording', name='recording'),
    url(r'^save/', 'action.views.save', name='save'),
    url(r'^register/', 'action.views.register', name='register'),
    # url(r'^slowmotion/', include('slowmotion.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

if settings.LOCAL_DEV:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT}))

