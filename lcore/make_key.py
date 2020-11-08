from django.core.management.utils import get_random_secret_key

new_key = '%'
while new_key.__contains__('%'):
    new_key = get_random_secret_key()
print(get_random_secret_key())