from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'ribbit_app.views.index'), # root
    url(r'^login$', 'ribbit_app.views.login_view'), # login
    url(r'^logout$', 'ribbit_app.views.logout_view'), # logout
    url(r'^signup$', 'ribbit_app.views.signup'), # signup
    url(r'^ribbits$', 'ribbit_app.views.public'), # public ribbits
    url(r'^submit$', 'ribbit_app.views.submit'), # submit new ribbit
)
