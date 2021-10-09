# Generated by Django 3.2.7 on 2021-10-09 06:01

import Posts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0005_auto_20211009_0558'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='content',
            field=Posts.models.Base64Field(db_column='content', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='post',
            name='post_pk',
            field=models.CharField(default='2f1444aad8d84b0da59528e032c2b148', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
    ]