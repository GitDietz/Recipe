import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    class Meta:
        model = Recipe
        fields = {
            'name': ['icontains', ],
            'cuisine__name': ['icontains', ],
            'meal_category__name' : ['icontains', ],
            #'in_book': ['icontains', ],
        }

