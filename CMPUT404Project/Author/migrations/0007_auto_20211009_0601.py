# Generated by Django 3.2.7 on 2021-10-09 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0006_auto_20211009_0558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='auth_pk',
            field=models.CharField(default='ebf4e1ad204c4a1ca39080059cdbea6d', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.CharField(default='http://127.0.0.1:8000/author/ebf4e1ad204c4a1ca39080059cdbea6d', editable=False, max_length=200),
        ),
        migrations.AlterField(
            model_name='author',
            name='url',
            field=models.CharField(default='http://127.0.0.1:8000/author/ebf4e1ad204c4a1ca39080059cdbea6d', editable=False, max_length=200),
        ),
    ]
