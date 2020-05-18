from django.urls import path, re_path

from .views import *

app_name = 'the_list'

urlpatterns = [
    # path('list/', recipe_list, name='recipe_list'),
    path('filter/', recipe_filter, name='recipe_filter'),
    re_path('recipe/(?P<pk>\d+)', recipe_detail, name='recipe_detail'),
    # path('create/', shop_create, name='shop_create'),
    # #url(r'bogger/$', shop_create, name='shop_bogger'),
    # #url(r'groups/(?P<pk>\d+)$', group_detail, name='group_update'),
    # path('groups/create', group_detail, name='group_create'),
    # re_path('groups/delete/(?P<pk>\d+)', group_delete, name='group_delete'),
    # re_path('groups/maintain/(?P<pk>\d+)', group_maintenance, name='group_maintenance'),
    # re_path('groups/make_leader/(?P<pk>\d+)(?P<sep>#)(?P<user_id>\d+)', group_make_leader, name='group_make_leader'),
    # re_path('groups/add_member/(?P<pk>\d+)(?P<sep>#)(?P<user_id>\d+)', group_add_member, name='group_add_member'),
    # re_path('groups/remove_self/(?P<pk>\d+)', group_remove_self, name='group_remove_self'),
    # re_path('groups/remove_leader/(?P<pk>\d+)(?P<sep>#)(?P<user_id>\d+)', group_remove_leader, name='group_remove_leader'),
    # re_path('groups/remove_member/(?P<pk>\d+)(?P<sep>#)(?P<user_id>\d+)', group_remove_member, name='group_remove_member'),
    # path('groups/', group_list, name='group_list'),
    # path('group_select/', user_group_select, name='group_select'),
    path('books/', book_list, name='book_list'),
    path('book/create/', book_create, name='book_create'),
    re_path('foodgroup/(?P<pk>\d+)', foodgroup_detail, name='foodgroup_detail'),
    path('foodgroup_list/', foodgroup_list, name='foodgroup_list'),
    path('home/',home,name='home'),
    re_path('ingredient/(?P<pk>\d+)', ingredient_detail, name='ingredient_detail'),
    path('ingredient_list/', ingredient_list, name='ingredient_list'),
    path('ingredient_lookup/', ingredient_lookup, name='ingredient_lookup'),
    path('load', recipe_load, name='recipe_load'),
    # re_path('merchants/(?P<pk>\d+)', merchant_update, name='merchant_update'),
    # re_path('merchants/delete/(?P<pk>\d+)', merchant_delete, name='merchant_delete'),
    # re_path('(?P<pk>\d+)/', shop_detail, name='shop_edit'),
    # path('support/', support, name='support'),
    # path('users/', search, name='user_list'),
    # path('filter/', simple_item_list, name='filter_list'),
    # url(r'(?P<id>\d+)/$', item_detail, name='edit'),
]
