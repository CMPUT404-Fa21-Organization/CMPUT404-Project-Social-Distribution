# Generated by Django 3.2.7 on 2021-10-27 17:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Author', '0002_inbox_iposts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inbox',
            name='auth_pk',
            field=models.OneToOneField(default='b4c4864e37f84427b743fea0524e5c4a', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='like',
            name='like_id',
            field=models.CharField(default='c53ae3a608494694aa93104907d1ddf3', editable=False, max_length=200, primary_key=True, serialize=False),
        ),
    ]
