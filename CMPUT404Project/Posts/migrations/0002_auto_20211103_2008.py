# Generated by Django 3.2.7 on 2021-11-03 20:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment_pk',
            field=models.CharField(default='a3a5c9cde6dc4dd1bac6e36d77eef3c6', editable=False, max_length=100, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='categories',
            field=models.CharField(choices=[('Web', 'Web'), ('Tutorial', 'Tutorial'), ('', '')], max_length=20),
        ),
    ]
