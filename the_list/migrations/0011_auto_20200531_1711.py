# Generated by Django 3.0.4 on 2020-05-31 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('the_list', '0010_recipe_meal_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cuisine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='cuisine',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='the_list.Cuisine'),
        ),
    ]
