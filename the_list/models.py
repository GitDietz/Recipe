from admin_auto_filters.filters import AutocompleteFilter
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.db import models
from django.db.models.functions import Lower
from django.conf import settings


# ## Model Managers ## #
class CatManager(models.Manager):
    def all(self):
        qs = super(CatManager, self).all()
        return qs


class CuisineManager(models.Manager):
    def all(self):
        qs = super(CuisineManager, self).all()
        return qs


class RecipeManager(models.Manager):
    def all(self):
        qs = super(RecipeManager, self).all()
        return qs

    def filter_by_instance(self, instance):
        obj_id = instance.id
        qs = super(RecipeManager, self).filter(object_id=obj_id)
        return qs

    def create_name_page(self, name, in_book, page):
        qs = super(RecipeManager, self).filter(name=name).filter(in_book=in_book).filter(page=page)
        if qs.exists():
            return None
        else:
            recipe = Recipe(name=name, in_book=in_book, page=page)
            recipe.save()
            return recipe


class BookManager(models.Manager):
    def all(self):
        qs = super(BookManager, self).all()
        return qs


class FoodGroupManager(models.Manager):
    def all(self):
        qs = super(FoodGroupManager, self).all()
        return qs


class IngredientManager(models.Manager):
    def all(self):
        qs = super(IngredientManager, self).all().order_by(Lower('name'))
        return qs


# class ShopGroupManager(models.Manager):
#     def all(self):
#         qs = super(ShopGroupManager, self).all()
#         return qs
#
#     def filter_by_instance(self, instance):
#         obj_id = instance.id
#         qs = super(ShopGroupManager, self).filter(object_id=obj_id)
#         return qs
#
#     def managed_by(self, user):
#         qs = super(ShopGroupManager, self).filter(manager=user)
#         return qs
#
#     def create_group(self, name, manager):
#         new_group = self.create(name=name, manager=manager, disabled = True)
#         return new_group
#
#     def member_of(self, user):
#         qs = super(ShopGroupManager, self).filter(members=user)
#         return qs
#
#     def leaders(self, user):
#         qs = super(ShopGroupManager, self).filter(leaders=user)
#         return qs

# ## Models ## #

# class ShopGroup(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     purpose = models.CharField(max_length=200, blank=False)
#     date_added = models.DateTimeField(auto_now=False, auto_now_add=True)
#     manager = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, related_name='manage_by', on_delete=models.CASCADE)
#     members = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='member_of')
#     leaders = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='leader_of')
#     disabled = models.BooleanField(default=False)
#     objects = ShopGroupManager()
#
#     class Meta:
#         ordering = ['name']
#
#     def __str__(self):
#         return self.name.title()
#
#     def activate(self):
#         self.disabled = False
#
#     @property
#     def info(self):
#         label = f'Created by {self.manager} - {self.purpose}'
#         return label


class Book(models.Model):
    name = models.CharField(max_length=150, unique=False, blank=False)
    author = models.CharField(max_length=50, unique=False, blank=False)
    date_added = models.DateField(auto_now=False, auto_now_add=True)
    objects = BookManager()

    class Meta:
        ordering = ['name']
        # unique_together = ('name', 'for_group')
        # indexes = [models.Index(fields=['name', 'for_group'])]

    def __str__(self):
        return f'{self.name.title()}'

    def __repr__(self):
        return self.name.title()


class Category(models.Model):
    """
    Like Main/starter / drink etc
    """
    name = models.CharField(max_length=50, unique=True, blank=False)
    objects = CatManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name.title()}'

    def __repr__(self):
        return self.name.title()


class Cuisine(models.Model):
    """
    Quisine names
    """
    name = models.CharField(max_length=50, unique=True, blank=False)
    objects = CuisineManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name.title()}'

    def __repr__(self):
        return self.name.title()


class FoodGroup(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    objects = FoodGroupManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        label = self.name.title()
        return str(label)

    def get_absolute_url(self):
        return reverse('recipe:foodgroup_detail', args=[str(self.id)])


class Friend(models.Model):
    # NICK NAME should be unique
    nick_name = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    likes = models.CharField(max_length=250)
    dob = models.DateField(auto_now=False, auto_now_add=False)
    lives_in = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return self.nick_name


class Ingredient(models.Model):
    name = models.CharField(max_length=50, unique=True, blank=False)
    belong_to = models.ForeignKey(FoodGroup, null=True, on_delete=models.CASCADE)
    objects = IngredientManager()

    def __str__(self):
        label = self.name.title()
        return str(label)

    def get_absolute_url(self):
        # return '/recipe/ingredient/%i/' % self.id
        return reverse('recipe:ingredient_detail', args=[str(self.id)])


class Recipe(models.Model):
    name = models.CharField(max_length=150, unique=False, blank=False)
    description = models.CharField(max_length=100, blank=True)
    main_ingredients = models.CharField(max_length=200, unique=False, blank=True)
    notes = models.CharField(max_length=100, blank=True)
    stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    meal_category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    cuisine = models.ForeignKey(Cuisine, null=True, on_delete=models.PROTECT)
    in_book = models.ForeignKey(Book, blank=True, null=True, on_delete=models.CASCADE)
    recipe_file = models.FileField(upload_to='data', blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)

    objects = RecipeManager()

    class Meta:
        ordering = ['description']
        indexes = [models.Index(fields=['name', 'in_book', 'page']), ]
        unique_together = [['name', 'in_book', 'page']]


    def __str__(self):
        label = self.name.title()
        return str(label)

    def get_absolute_url(self):
        return reverse("recipe:recipe_detail", args=[str(self.id)])


class Comments(models.Model):
        made_on = models.DateField(auto_now_add=True, auto_now=False)
        tried_it = models.BooleanField(default=False, null=False)
        comment_made = models.CharField(max_length=150, unique=False, blank=True, null=False)
        about_recipe = models.ForeignKey(Recipe, null=False, on_delete=models.CASCADE)

        class Meta:
            ordering = ['-made_on']

        def __str__(self):
            return f'{self.made_on} : {self.comment_made}'

        def __repr__(self):
            return f'{self.comment_made}'

    # @property
    # def to_purchase(self):
    #     if self.date_purchased is None and self.cancelled is None:
    #         return True
    #     else:
    #         return False
    #
    # @property
    # def name_qty(self):
    #     if len(self.quantity) > 0:
    #         return f'{self.description} [{self.quantity}]'
    #     else:
    #         return self.description



