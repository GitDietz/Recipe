from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from act.views import *


urlpatterns = [
    # re_path('activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/(?P<group>[0-9A-Za-z_\-]+)/',
    #         activate, name='activate'),
    # path('activation_sent/', account_activation_sent, name='account_activation_sent'),
    path('admin/', admin.site.urls),
    # path('complete/', complete, name='complete'),
    # # path('invite/', include(('invitation.urls', 'invitation'), namespace='invitations')),
    # path('invite/', invite, name='invite'),
    # re_path('invited/(?P<key>[0-9a-zA-Z]{40})/', invited, name='invited'),
    # path('invite_select_view/', invite_select_view, name='invite_select_view'),
    path('login/', login_email, name='login'),
    path('logout/', logout_view, name='logout'),
    # path('password_link_sent/', password_link_sent, name='password_link_sent'),
    # re_path('pset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', password_validation, name='password_validation'),
    path('register/', register_view, name='register'),
    # path('set_group/', set_group, name='set_group'),
    path('recipe/', include(('the_list.urls', 'recipe'), namespace='recipe')),
    path('', home_view, name='home'),
    ]

if settings.DEBUG:      # ensures that this will only be done in DEV
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




