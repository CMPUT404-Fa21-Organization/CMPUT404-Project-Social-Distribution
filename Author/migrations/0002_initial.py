# Generated by Django 3.2.7 on 2021-12-01 03:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Author', '0001_initial'),
        ('Posts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='inbox',
            name='iPosts',
            field=models.ManyToManyField(blank=True, default=list, to='Posts.Post'),
        ),
        migrations.AddField(
            model_name='followers',
            name='items',
            field=models.ManyToManyField(blank=True, default=list, related_name='items', to=settings.AUTH_USER_MODEL),
        ),
    ]