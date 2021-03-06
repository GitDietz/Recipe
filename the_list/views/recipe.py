from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import DatabaseError
from django.db.models import Q

from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, Http404, redirect, HttpResponse
from django.urls import reverse
from urllib.parse import urlencode

import csv, io, json
import logging

from the_list.filter import RecipeFilter
from the_list.forms import *
from the_list.models import Book, Recipe, FoodGroup


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
        form = RecipeForm(request.POST, request.FILES, instance=obj)
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
    # remove this to a function later
    get_dict = request.GET.copy()
    try:
        del get_dict['page']
    except KeyError:
        pass

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