# Generated by Django 3.2.7 on 2021-10-27 17:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_pk',
            field=models.CharField(default='3c9a11dc645a4d9281f2f0bada413386', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
    ]
