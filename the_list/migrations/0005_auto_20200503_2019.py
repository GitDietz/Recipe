# Generated by Django 3.0.4 on 2020-05-03 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('the_list', '0004_auto_20200503_1913'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='recipe',
            unique_together={('name', 'in_book', 'page')},
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['name', 'in_book', 'page'], name='the_list_re_name_fddca8_idx'),
        ),
    ]
