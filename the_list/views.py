from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import DatabaseError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, Http404, redirect, HttpResponse
from django.urls import reverse
from urllib.parse import urlencode

import csv, io, json
import logging

from .filter import RecipeFilter
from .forms import *
from .models import Book, Recipe, FoodGroup

from lcore.utils import *

from datetime import date

#  #################################  Recipe #################################


def foodgroup_detail(request, pk=None):
    # if pk = 0 then it is to create a new item - modify the flow for that

    if pk == '0':
        object = None
    else:
        object = get_object_or_404(FoodGroup, pk=pk)

    if request.method == "POST":
        form = FoodGroupForm(request.POST, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recipe:foodgroup_list'))

    template_name = 'item_detail.html'
    context = {
        'title': 'Update Item',
        'form': FoodGroupForm(instance=object),
        'notice': '',
    }
    return render(request, template_name, context)


def foodgroup_list(request):
    """
    Will show the food group list
    """
    fg_qs = FoodGroup.objects.all()
    template = 'ingredient_list.html'
    title = 'List of Food Groups'
    addition_text = 'Add Foodgroup'
    add_url = 'recipe:foodgroup_detail'
    context = {
        'title': title,
        'object_list': fg_qs,
        'add_text': addition_text,
        'new_item_url': add_url,
    }
    return render(request,template,context)


def indexView(request):
    # url = friend/'
    form = FriendForm()
    friends = Friend.objects.all()
    return render(request, "index.html", {"form": form, "friends": friends})


def checkNickName(request):
    """feature of the postfriend function, not part of recipe project per se"""
    # request should be ajax and method should be GET.
    if request.is_ajax and request.method == "GET":
        # get the nick name from the client side.
        nick_name = request.GET.get("nick_name", None)
        # check for the nick name in the database.
        if Friend.objects.filter(nick_name = nick_name).exists():
            # if nick_name found return not valid new friend
            return JsonResponse({"valid":False}, status = 200)
        else:
            # if nick_name not found, then user can create a new friend.
            return JsonResponse({"valid":True}, status = 200)

    return JsonResponse({}, status = 400)


def postFriend(request):
    # url = friend/ajax/ '
    # request should be ajax and method should be POST.
    if request.is_ajax and request.method == "POST":
        # get the form data
        form = FriendForm(request.POST)
        # save the data and after fetch the object in instance
        if form.is_valid():
            instance = form.save()
            # serialize in new friend object in json
            ser_instance = serializers.serialize('json', [ instance, ])
            # send to client side.
            return JsonResponse({"instance": ser_instance}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": form.errors}, status=400)

    # some error occured
    return JsonResponse({"error": ""}, status=400)


def ingredient_detail(request, pk=None):
    # if pk = 0 then it is to create a new item - modify the flow for that
    # now working this as  html only form not rendered
    if pk == '0':
        object = None
    else:
        object = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":
        form = IngredientForm(request.POST, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recipe:ingredient_list'))

    template_name = 'item_detail.html'
    context = {
        'title': 'Update Item',
        'form': IngredientForm(instance=object),
        'notice': '',
    }
    return render(request, template_name, context)


def ingredient_detail_original(request, pk=None):
    # if pk = 0 then it is to create a new item - modify the flow for that
    if pk == '0':
        object = None
    else:
        object = get_object_or_404(Ingredient, pk=pk)

    if request.method == "POST":
        form = IngredientForm(request.POST, instance=object)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recipe:ingredient_list'))

    template_name = 'item_detail.html'
    context = {
        'title': 'Update Item',
        'form': IngredientForm(instance=object),
        'notice': '',
    }
    return render(request, template_name, context)


def ingedient_delete(request, pk):
    obj = get_object_or_404(Ingredient, pk=pk)
    if obj:
        obj.delete()
    return HttpResponseRedirect(reverse('recipe:ingredient_list'))


def ingredient_dropdown(request):
    q = request.GET.get('term', None)
    print(f'the ajax call ingredient in ingredient_dropdown = {q}')
    ingredients = list(Ingredient.objects.filter(name__icontains=q))
    return render(request, 'ingredient_dropdown.html', {'ingredients': ingredients})


def ingredient_list(request):
    """
    Will show the ingredients list
    """
    #ingredient_qs = Ingredient.objects.all().filter(belong_to__isnull=True)
    ingredient_qs = Ingredient.objects.all()
    template = 'ingredient_list.html'
    title = 'List of Ingredients'
    addition_text = 'Add Ingredient'
    add_url = 'recipe:ingredient_detail'
    list_for = 'ingredient'
    context = {
        'title': title,
        'object_list': ingredient_qs,
        'add_text': addition_text,
        'new_item_url': add_url,
        'list_for': list_for,
    }
    return render(request, template, context)


def ingredient_add_ajax(request):
    #  http://127.0.0.1:8000/recipe/ingredient_lookup/?term=ch
    if request.is_ajax:
        q = request.GET.get('item', None)
        print(f'the ajax call ingredient = {q}')
        ingredients = Ingredient.objects.filter(name__icontains=q).order_by('name')
        if ingredients.count() == 0:
            try:
                _, created = Ingredient.objects.get_or_create(name=q.strip().title())
                data = 'pass'
            except:
                data = 'fail'
        else:
            data = 'fail'
    else:
        data = 'fail'

    print(data)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def ingredient_lookup(request):
    #  http://127.0.0.1:8000/recipe/ingredient_lookup/?term=ch
    if request.is_ajax:
        q = request.GET.get('term', None)
        print(f'the ajax call ingredient = {q}')
        ingredients = Ingredient.objects.filter(name__icontains=q).order_by('name')
        results = []
        for ind in ingredients:
            ind_json = {}
            ind_json = ind.name
            results.append(ind_json)
        data = json.dumps(results)
    else:
        data = 'fail'

    print(data)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def recipe_detail(request, pk=None):
    # if pk = 0 then it is to create a new item - modify the flow for that
    if pk == '0':
        obj = None
    else:
        obj = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        form = RecipeForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('recipe:recipe_list'))

    template_name = 'recipe_detail.html'
    context = {
        'title': 'Update Item',
        'form': RecipeForm(instance=obj),
        'notice': '',
    }
    return render(request, template_name, context)


# @login_required
def recipe_list(request):
    """
    shows the list of items in the particular list, handles pagination as well
    """
    notice = ''
    logging.getLogger("info_logger").info(f"user = {request.user.username}")
    recipes = Recipe.objects.all().order_by('name')
    #recipes = Recipe.objects.all().filter(main_ingredients__isnull=True).order_by('name')
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
    shows the list of recipes filter but no pagination
    """
    notice = ''
    logging.getLogger("info_logger").info(f"user = {request.user.username}")
    recipes = Recipe.objects.all().order_by('name')
    # recipes = Recipe.objects.all().filter(main_ingredients__exact='').order_by('in_book', 'page')
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


def load_ingredients(request):
    """using the data from recipes to split values and add them to ingredients list"""
    recipes = Recipe.objects.all()
    ingrs = list(Ingredient.objects.all().values_list('name', flat=True))
    for recipe in recipes:
        if recipe.description != "":
            if '/' in recipe.description:
                x = recipe.description.split('/')
            else:
                x = recipe.description.split()
            print(x)
            if x:
                for item in x:
                    if item.strip() not in ingrs and item != 'and':
                        ingrs.append(item)
                        _, created = Ingredient.objects.get_or_create(name=item.strip())

    return render(request, 'done.html',{})


def home(request):
    """for the experiment on the setup of all the form tags"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            pass  # does nothing, just trigger the validation
    else:
        form = ContactForm()
    return render(request, 'experiment.html', {'form': form})


def home_colors(request):
    if request.method == 'POST':
        form = ColorfulContactForm(request.POST)
        if form.is_valid():
            pass  # does nothing, just trigger the validation
    else:
        form = ContactForm()
    return render(request, 'experiment_2.html', {'form': form})