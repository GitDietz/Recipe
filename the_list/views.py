from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from django.db import DatabaseError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, Http404, redirect
from urllib.parse import urlencode

import csv, io
import logging

from .filter import RecipeFilter
from .forms import *
from .models import Book, Recipe

from lcore.utils import *

from datetime import date


# def get_session_list_choice(request):
#     """
#     get the list choice from session or set it using the first group this user is in
#     handle the odd case when user is not in a group - should not happen outside DEV
#     """
#     try:
#         logging.getLogger("info_logger").info("get session choice")
#         list_active = request.session['list'] # the session can contain value that is no longer in DB
#         if list_active != '':
#             logging.getLogger("info_logger").info(f"session value = {list_active}")
#             if ShopGroup.objects.filter(id=list_active).exists():
#                 return list_active
#             else:
#                 logging.getLogger("info_logger").info('No such value in DB, new selection required')
#                 request.session.pop('list')
#                 return None
#         else:
#             logging.getLogger("info_logger").info(f"session NO value = {list_active}")
#             return None
#     except KeyError:
#         logging.getLogger("info_logger").info(f'no list in session, getting first option from DB')
#         list_choices = ShopGroup.objects.filter(members=request.user)
#         if list_choices:
#             select_item = list_choices.first().id
#             request.session['list'] = select_item
#             return select_item
#         else:
#             return None


#  #################################  Recipe #################################
# @login_required
# def shop_create(request):
#     """
#     responds to the item create template
#     if 'add multiple items' is selected on the submit button the same submission form will return
#     else the list view will be returned
#     """
#     logging.getLogger("info_logger").info(f"view entered | user = {request.user.username}")
#     list_choices, user_list_options, list_active_no, active_list_name = get_user_list_property(request)
#     form = ItemForm(request.POST or None, list=list_active_no)
#     title = 'Add purchase items'
#     notice = ''
#     if form.is_valid():
#         logging.getLogger("info_logger").info(f"form valid | user = {request.user.username}")
#
#         # get the objects still to purchase and check if this new one is among them
#         qs_tobuy = Item.objects.to_get()
#         item = form.save(commit=False)
#         this_found = qs_tobuy.filter(Q(description__iexact=item.description))
#         for_group = ShopGroup.objects.filter(id=list_active_no).first()
#         if this_found:
#             logging.getLogger("info_logger").info(f"item exists | user = {request.user.username}")
#             notice = 'Already listed : ' + item.description
#         else:
#             logging.getLogger("info_logger").info(f"item will be added | user = {request.user.username}")
#             item.in_group = for_group
#             item.description = item.description.title()
#             item.requested = request.user
#             # vendor_id=request.POST.get('vendor_select') #this returns the relevant ID i selected
#             vendor_id = item.to_get_from
#             # this_merchant = Merchant.objects.get(pk=vendor_id)
#             logging.getLogger("info_logger").info(f"item saving for vendor = {vendor_id}")
#             item.to_get_from = vendor_id  # this_merchant
#             item.date_requested = date.today()
#             item.save()
#             notice = 'Added ' + item.description
#
#         if 'add_one' in request.POST:
#             return redirect('shop:shop_list')
#         else:
#             form = ItemForm(None, list=list_active_no)
#
#     context = {
#         'title': title,
#         'form': form,
#         'notice': notice,
#         'selected_list': active_list_name,
#         'no_of_lists': user_list_options,
#     }
#     return render(request, 'item_create.html', context)


def ingredient_detail(request, pk=None):
    object = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":

        form = IngredientForm(request.POST, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recipe:ingredient_list'))

    template_name = 'ingredient_detail.html'
    context = {
        'title': 'Update Item',
        'form': IngredientForm(instance=object),
        'notice': '',
    }
    return render(request, template_name, context)


def ingredient_list(request):
    """
    Will show the ingredients list
    """
    ingredient_qs = Ingredient.objects.all()
    template = 'ingredient_list.html'
    title = 'List of Ingredients'
    context = {
        'title': title,
        'object_list': ingredient_qs,
    }
    return render(request,template,context)



# @login_required
def recipe_list(request):
    """
    shows the list of items in the particular list
    """
    notice = ''
    logging.getLogger("info_logger").info(f"user = {request.user.username}")
    recipes = Recipe.objects.all().order_by('name')
    # need to extract the part of the GET
    print(request.GET)
    # remove this to a function later
    get_dict = request.GET.copy()
    try:
        del get_dict['page']
    except KeyError:
        print('No page indicator on GET')

    recipes_filtered = RecipeFilter(get_dict, queryset=recipes)
    recipe_qs = recipes_filtered.qs
    page = request.GET.get('page', 1)
    paginator = Paginator(recipe_qs, 30)
    try:
        recipe_page = paginator.page(page)
    except PageNotAnInteger:
        recipe_page = paginator.page(1)
    except EmptyPage:
        recipe_page = paginator.page(paginator.num_pages)

    # consider startup nothing in the list
    context = {
        'title': 'Recipe list',
        'object_list': recipe_page,
        'filter_form': recipes_filtered,
        'notice': notice,
    }
    return render(request, 'recipe_list.html', context)


def recipe_filter(request):
    """
    shows the list of unfulfilled items in the particular list
    """
    notice = ''
    logging.getLogger("info_logger").info(f"user = {request.user.username}")
    recipes = Recipe.objects.all().order_by('name')
    print(request.GET)
    recipes_filtered = RecipeFilter(request.GET, queryset=recipes)
    # page = request.GET.get('page', 1)
    # paginator = Paginator(recipes_filtered, 30)
    # try:
    #     recipe_page = paginator.page(page)
    # except PageNotAnInteger:
    #     recipe_page = paginator.page(1)
    # except EmptyPage:
    #     recipe_page = paginator.page(paginator.num_pages)

    # consider startup nothing in the list
    context = {
        'title': 'Recipe list',
        'object_list': recipes_filtered,
        'notice': notice,
    }
    return render(request, 'filter_list.html', context)


# @login_required
# def recipe_detail(request, pk):
#     """
#     allows the edit of the item if its the requestor or the leader/s of the group
#     :param pk: for the instance of the item
#     :param request:
#     :return: divert to shoplist
#     """
#     logging.getLogger("info_logger").info(f"user = {request.user.username}")
#     item = get_object_or_404(Recipe, pk=pk)
#     active_list = item.in_group.id
#     user_is_leader = False
#     if request.user in item.in_group.leaders.all():
#         user_is_leader = True
#
#     if request.user == item.requested or user_is_leader:
#         if request.method == "POST":
#             logging.getLogger("info_logger").info(f"Posted form | user = {request.user.username}")
#             form = ItemForm(request.POST, instance=item, list=active_list)
#             if form.is_valid():
#                 logging.getLogger("info_logger").info(f"valid form submitted | user = {request.user.username}")
#                 form.save()
#                 return HttpResponseRedirect(reverse('shop:shop_list'))
#
#         template_name = 'item_detail.html'
#         context = {
#             'title': 'Update Item',
#             'form': ItemForm(instance=item, list=active_list),
#             'notice': '',
#         }
#         return render(request, template_name, context)
#     else:
#         logging.getLogger("info_logger").info(f"diverting to the list view | user = {request.user.username}")
#         return redirect('shop:shop_list')


# ################################# Book #################################


# @login_required
def book_list(request):
    logging.getLogger("info_logger").info(f'user = {request.user.username}')
    # list_choices, user_list_options, list_active_no, active_list_name = get_user_list_property(request)
    queryset_list = Book.objects.all()
    notice = ''
    context = {
        'title': 'Book List',
        'object_list': queryset_list,
        'notice': notice,
    }
    return render(request, 'book_list.html', context)


# @login_required
# def merchant_detail(request, id=None):
#     # 10/1/20 mod to use list as part of merchant model
#     logging.getLogger("info_logger").info(f'user = {request.user.username}')
#     instance = get_object_or_404(Merchant, id=id)
#     form = MerchantForm(request.POST or None)
#     list_choices, user_list_options, list_active_no, active_list_name = get_user_list_property(request)
#     title = 'Add or Edit Merchant'
#     notice = ''
#     if request.method == 'POST' and form.is_valid():
#         logging.getLogger("info_logger").info(f'valid form')
#
#         qs = Merchant.objects.all()
#         form.save(commit=False)
#         this_found = qs.filter(Q(name__iexact=Merchant.name))
#         if this_found:
#             logging.getLogger("info_logger").info(f'Merchant already in list')
#             notice = 'Already listed ' + Merchant.name.title()
#         else:
#             logging.getLogger("info_logger").info(f'ok will add {Merchant.name} to list')
#             Merchant.name = Merchant.title()
#             # Adding list reference
#             Merchant.for_group = active_list_name
#             Merchant.save()
#             notice = 'Added ' + Merchant.name
#
#         return redirect('shop:merchant_list')
#
#     context = {
#         'title': title,
#         'form': form,
#         'notice': notice,
#         'instance': instance
#     }
#     return render(request, 'book.html', context)


# @login_required
def book_create(request):
    form = BookForm(request.POST or None)
    if request.method == "POST":
        logging.getLogger("info_logger").info(f'from submitted')
        if form.is_valid():
            try:
                book = form.save(commit=False)
                book.name = form.cleaned_data['name'].title()
                book.author = form.cleaned_data['author'].title()
                book.save()
                return redirect('recipe:book_list')
            except DatabaseError:
                raise ValidationError('That Book already exists in this group')
        else:
            logging.getLogger("info_logger").info(f'Error on form {form.errors}')

    template_name = 'book.html'
    context = {
        'title': 'Create Book',
        'form': form,
        'notice': '',
    }
    return render(request, template_name, context)


# @login_required
# def merchant_update(request, pk):
#     merchant = get_object_or_404(Merchant, pk=pk)
#     list = merchant.for_group
#     if request.method == "POST":
#         logging.getLogger("info_logger").info(f'form submitted')
#         form = MerchantForm(request.POST, instance=merchant, list=list.id, default=list)
#         if form.is_valid():
#             form.save()
#             logging.getLogger("info_logger").info(f'complete - direct to list')
#             return HttpResponseRedirect(reverse('shop:merchant_list'))
#
#     template_name = 'book.html'
#     context = {
#         'title': 'Update Merchant',
#         'form': MerchantForm(instance=merchant, list=list.id, default=list),
#         'notice': '',
#     }
#     return render(request, template_name, context)
#
#
# @login_required
# def merchant_delete(request, pk):
#     merchant = get_object_or_404(Merchant, pk=pk)
#     # users = User.objects.all()
#     # if the user is a leader then allow to remove a group
#
#     if request.method == 'POST':
#         this_group = merchant.for_group
#         leader = is_user_leader(request, this_group.id)
#         if leader:
#             merchant.delete()
#             logging.getLogger("info_logger").info(f'merchant deleted')
#         return HttpResponseRedirect(reverse('shop:merchant_list'))
#
#     template_name = 'merchant_delete.html'
#     context = {
#         'title': 'Delete Merchant',
#         'object': merchant,
#         'notice': '',
#     }
#     return render(request, template_name, context)

# @permission_required('admin.can_add_log_entry')

def recipe_load(request):
    template = 'upload.html'
    message = ''
    context = {'title': 'set loading file',
               'message': message,
               }
    if request.method == "GET":
        return render(request, template, context)

    csv_file = request.FILES['file']

    if not csv_file.name.endswith('.csv'):
        message = 'Only CSV'

    this_book = get_object_or_404(Book, pk=3)
    data_set = csv_file.read().decode('UTF-8')
    io_string = io.StringIO(data_set)
    next(io_string)
    for column in csv.reader(io_string, delimiter=',', quotechar='|'):
        if int(column[1]) > 62:
            try:
                # _, created = Recipe.objects.update_or_create(name=column[0],
                #                                         description=column[1],
                #                                         main_ingredient=column[2],
                #                                         category=column[3],
                #                                         in_book=this_book,
                #                                         page=column[4])
                print(column)
                # obj = Recipe.objects.create_name_page(name=column[0].strip(),
                #                                       # description='',
                #                                       # main_ingredient='',
                #                                       # category='',
                #                                       in_book=this_book,
                #                                       page=int(column[1]))
                _, created = Recipe.objects.get_or_create(name=column[0].strip(),
                                                             description='',
                                                             main_ingredient='',
                                                             category='',
                                                             in_book=this_book,
                                                             page=int(column[1]))
            except:
                print(f'{Exception} on row with name {column[0]}')

    context = {}
    return render(request, template, context)
