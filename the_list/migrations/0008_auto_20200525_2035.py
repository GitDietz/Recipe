# Generated by Django 3.0.4 on 2020-05-25 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('the_list', '0007_friend'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='main_ingredient',
        ),
        migrations.AddField(
            model_name='recipe',
            name='main_ingredients',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
