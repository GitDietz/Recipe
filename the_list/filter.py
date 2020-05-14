import django_filters

from .models import Recipe


class RecipeFilter(django_filters.FilterSet):
    class Meta:
        model = Recipe
        fields = {
            'name': ['icontains', ],
            'category': ['icontains', ],
            #'in_book': ['icontains', ],
        }

