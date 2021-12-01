# Generated by Django 3.2.7 on 2021-12-01 15:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0003_auto_20211130_2055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='followers',
            name='auth_pk',
            field=models.OneToOneField(default='c5ef243368c54f81a1794cbcf19c91a5', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='inbox',
            name='auth_pk',
            field=models.OneToOneField(default='3b971c9ef45a4afd96af5763d9dc8d1f', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
