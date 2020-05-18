from dal import autocomplete
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from django.utils.safestring import mark_safe
from .models import Book, FoodGroup, Ingredient, Recipe


# class SelectDropdownWidget(forms.Select):
#     class Media:
#         css = {
#             'all': (
#                 iasettings.MEDIA_URL + 'js/selectmenu/ui.selectmenu.css',
#             )
#         }
#         js = (
#             iasettings.MEDIA_URL + 'js/selectmenu/ui.selectmenu.js',
#         )
#
#     def __init__(self, language=None, attrs=None):
#         self.language = language or settings.LANGUAGE_CODE[:2]
#         super(SelectDropdownWidget, self).__init__(attrs=attrs)
#
#     def render(self, name, value, attrs=None):
#         rendered = super(SelectDropdownWidget, self).render(name, value, attrs)
#         return rendered + mark_safe(u'''<script type="text/javascript">
#             $(document).ready(function afterReady() {
#                 var elem = $('#id_%(name)s');
#                 elem.selectmenu();
#             });
#             </script>''' % {'name':name})


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = [
            'name',
            'author',
        ]

    # def __init__(self, *args, **kwargs):
    #
    #     active_list = Merchant.objects.filter(for_group_id=list)
    #
    #     # super(ItemForm, self).__init__(*args, **kwargs)
    #     super().__init__(*args, **kwargs)
    #     self.fields['to_get_from'].queryset = active_list
    #     # not used part of the readonly
    #     # self.fields['requested'].widget.attrs['readonly'] = True
    #
    # def clean_description(self):
    #     return self.cleaned_data['description'].title()
    #
    # def clean_to_get_from(self):
    #     return self.cleaned_data['to_get_from']
    #
    # def clean_quantity(self):
    #     return self.cleaned_data['quantity']


class FoodGroupForm(forms.ModelForm):

    class Meta:
        model = FoodGroup
        fields = ('__all__')


class IngredientForm(forms.ModelForm):
    # belong_to = forms.ModelChoiceField(
    #     queryset=FoodGroup.objects.all(),
    #     widget=autocomplete.ListSelect2(url='test:fg-autocomplete')
    # )

    class Meta:
        model = Ingredient
        fields = ('__all__')


class RecipeForm(forms.ModelForm):
    ingredient_add = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'ui-front', 'autocomplete': 'on'}))
    #div is id= id_ingredient_add

    class Meta:
        model = Recipe
        fields = ('__all__')


class ContactForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    message = forms.CharField(
        max_length=2000,
        widget=forms.Textarea(),
        help_text='Write here your message!'
    )
    source = forms.CharField(       # A hidden input for internal use
        max_length=50,              # tell from which page the user sent the message
        widget=forms.HiddenInput()
    )

    def clean(self):
        cleaned_data = super(ContactForm, self).clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        message = cleaned_data.get('message')
        if not name and not email and not message:
            raise forms.ValidationError('You have to write something!')