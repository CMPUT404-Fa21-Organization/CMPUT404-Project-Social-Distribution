# Generated by Django 3.2.7 on 2021-10-07 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0002_alter_post_post_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_pk',
            field=models.CharField(default='18e7e05846f040aa90062c5b47a959d5', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
    ]
