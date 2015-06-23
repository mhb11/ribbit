from django.conf.urls import patterns, include, url
from django.contrib import admin
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'ribbit_app.views.index'), # root
    url(r'^login$', 'ribbit_app.views.login_view'), # login
    url(r'^logout$', 'ribbit_app.views.logout_view'), # logout
    url(r'^signup$', 'ribbit_app.views.signup'), # signup
    url(r'^ribbits$', 'ribbit_app.views.public'), # public ribbits
    url(r'^submit$', 'ribbit_app.views.submit'), # submit new ribbit
    url(r'^users/$', 'ribbit_app.views.users'),
    url(r'^users/(?P<username>\w{0,30})/$', 'ribbit_app.views.users'),#<?P<username> captures the username queried via GET, and \w{0,30} asserts that max length for a username is 30 characters
    url(r'^follow$', 'ribbit_app.views.follow'),
)
