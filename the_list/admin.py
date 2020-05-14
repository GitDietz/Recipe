from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin

from .models import Book, Recipe, FoodGroup, Ingredient


class BookModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'author']

    class Meta:
        model = Book


admin.site.register(Book, BookModelAdmin)


class IngredientModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'belong_to']

    class Meta:
        model = Ingredient


admin.site.register(Ingredient, IngredientModelAdmin)



class FoodGroupAdmin(admin.ModelAdmin):
    list_display = ['name']

    class Meta:
        model = FoodGroup
        ordering = ['name', ]

admin.site.register(FoodGroup, FoodGroupAdmin)

#
# class RecipeFilter(AutocompleteFilter):
#     title = 'Recipe'
#     field_name = 'name'


# class RecipeAdmin(admin.ModelAdmin):
#


class RecipeModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'main_ingredient', 'category', 'in_book']
    search_fields = ['name']
    # list_filter = [RecipeFilter]

    class Meta:
        model = Recipe


admin.site.register(Recipe, RecipeModelAdmin)

#
# class ShopGroupModelAdmin(admin.ModelAdmin):
#     list_display = ['name']
#
#     class Meta:
#         model = ShopGroup
#
#
# admin.site.register(ShopGroup, ShopGroupModelAdmin)
