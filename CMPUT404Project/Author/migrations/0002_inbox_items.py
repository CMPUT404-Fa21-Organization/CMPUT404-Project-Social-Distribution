# Generated by Django 3.2.7 on 2021-10-20 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Posts', '0001_initial'),
        ('Author', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='items',
            field=models.ManyToManyField(blank=True, default=list, to='Posts.Post'),
        ),
    ]
