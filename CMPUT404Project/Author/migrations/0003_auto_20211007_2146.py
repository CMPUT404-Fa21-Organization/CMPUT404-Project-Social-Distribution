# Generated by Django 3.2.7 on 2021-10-07 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0002_auto_20211007_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='auth_pk',
            field=models.CharField(default='e6dee10bcd854343a66b89753fdd62d5', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.CharField(default='http://127.0.0.1:8000/author/e6dee10bcd854343a66b89753fdd62d5', editable=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='author',
            name='url',
            field=models.CharField(default='http://127.0.0.1:8000/author/e6dee10bcd854343a66b89753fdd62d5', editable=False, max_length=200),
        ),
    ]
