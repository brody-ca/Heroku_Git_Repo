from django.conf.urls import patterns, include, url
from django.contrib.auth.views import password_reset

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'application.posting_views.views.home'),
    url(r'^home$', 'application.posting_views.views.home'),
    url(r'^login$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
    url(r'^logout$', 'application.user_views.views.logout_user'),
    url(r'^register$', 'application.user_views.views.register'),
    url(r'^profile$', 'application.user_views.views.view_profile', name='view_profile'),
    url(r'^eprofile$', 'application.user_views.views.edit_profile', name='edit_profile'),
    url(r'^follows$', 'application.posting_views.views.get_followed_user_requests', name='get_followed_user_requests'),
    url(r'^follow_user$', 'application.user_views.views.follow_user', name='follow_user'),
    url(r'^view_request$', 'application.posting_views.views.view_request', name='view_request'),
    url(r'^new_request$', 'application.posting_views.views.new_request', name='new_request'),
    url(r'^my_requests$', 'application.posting_views.views.view_my_requests', name='view_my_requests'),
    url(r'^new_response$', 'application.posting_views.views.new_response', name='new_response'),
    url(r'^select_response$', 'application.posting_views.views.select_response', name='select_response'),
    url(r'^like_request/(\d+)$', 'application.posting_views.views.like_request', name='like_request'),
    url(r'^dislike_request/(\d+)$', 'application.posting_views.views.dislike_request', name='dislike_request'),
    url(r'^like_response/(\d+)$', 'application.posting_views.views.like_response', name='like_response'),
    url(r'^dislike_response/(\d+)$', 'application.posting_views.views.dislike_response', name='dislike_response'),    
    url(r'^change_password$', 'application.user_views.views.change_password'),
    url(r'^new_comment$', 'application.posting_views.views.new_comment', name='new_comment'),
    
    url(r'^password_reset$', 'django.contrib.auth.views.password_reset', {'post_reset_redirect' : '/user/password/reset/done/'}, name="password_reset"),
    url(r'^user/password/reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^user/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect' : '/user/password/done/'}),
    url(r'^user/password/done/$', 'django.contrib.auth.views.password_reset_complete'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
