# Generated by Django 3.0.4 on 2020-06-01 11:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('the_list', '0012_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='category',
        ),
    ]
