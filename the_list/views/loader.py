import csv, io, json

from django.shortcuts import render, get_object_or_404


from ..models import Recipe, Book, Ingredient


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
                # modify the load function based on the input file format
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

