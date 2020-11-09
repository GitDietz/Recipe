from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, re_path

from .views import experiments
from .views import loader, recipe

app_name = 'the_list'

urlpatterns = [
    path('list/', recipe.recipe_list, name='recipe_list'),
    #re_path('filter/', recipe_filter, name='recipe_filter'),
    re_path('recipe/(?P<pk>\d+)', recipe.recipe_detail, name='recipe_detail'),
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
    path('books/', recipe.book_list, name='book_list'),
    path('book/create/', recipe.book_create, name='book_create'),
    re_path('foodgroup/(?P<pk>\d+)', recipe.foodgroup_detail, name='foodgroup_detail'),
    path('foodgroup_list/', recipe.foodgroup_list, name='foodgroup_list'),
    path('friend/', experiments.indexView),
    path('friend/ajax/', experiments.postFriend, name="post_friend"),
    path('friend/checkNickName/', experiments.checkNickName, name='checkNickName'),
    path('home/', recipe.home, name='home'),
    path('home_colors/', recipe.home_colors, name='home_colors'),
    re_path('ingredient/(?P<pk>\d+)', recipe.ingredient_detail, name='ingredient_detail'),
    path('ingredient_add_ajax/', recipe.ingredient_add_ajax, name='ingredient_add_ajax'),
    re_path('ingedient_delete/(?P<pk>\d+)', recipe.ingedient_delete, name='ingedient_delete'),
    path('ingredient_dropdown', recipe.ingredient_dropdown, name='ingredient_dropdown'),
    path('ingredient_list/', recipe.ingredient_list, name='ingredient_list'),
    path('ingredient_lookup/', recipe.ingredient_lookup, name='ingredient_lookup'),
    path('load', loader.recipe_load, name='recipe_load'),
    path('load_ingredients', loader.load_ingredients, name='load_ingredients'),
    # re_path('merchants/(?P<pk>\d+)', merchant_update, name='merchant_update'),
    # re_path('merchants/delete/(?P<pk>\d+)', merchant_delete, name='merchant_delete'),
    # re_path('(?P<pk>\d+)/', shop_detail, name='shop_edit'),
    # path('support/', support, name='support'),
    # path('users/', search, name='user_list'),
    # path('filter/', simple_item_list, name='filter_list'),
    # url(r'(?P<id>\d+)/$', item_detail, name='edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

