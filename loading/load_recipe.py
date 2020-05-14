import csv
from the_list.models import Recipe

def run_load():
    file_handler = open('loadmartin.csv')
    reader = csv.reader(file_handler)

    for r in reader:
        print(r)
        # r, created = Recipe.objects.get_or_create(name=r[0], description=r[1], main_ingredient=r[2], category=r[3], in_book=1)
        r = Recipe(name=r[0], description=r[1], main_ingredient=r[2], category=r[3],in_book=1)
        r.save()
