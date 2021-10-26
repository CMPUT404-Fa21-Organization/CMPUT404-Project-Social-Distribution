# Generated by Django 3.2.7 on 2021-10-26 20:58

import Posts.commentModel
import Posts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_pk', models.CharField(default='d44d33ef97864ff68c8ba7d84be095a4', editable=False, max_length=100, primary_key=True, serialize=False)),
                ('author', models.JSONField(editable=False)),
                ('id', models.CharField(editable=False, max_length=200)),
                ('type', models.CharField(default='post', editable=False, max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('origin', models.CharField(blank=True, max_length=200)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('contentType', models.CharField(choices=[('markdown', 'text/markdown'), ('plain', 'text/plain'), ('app', 'application/base64'), ('png', 'image/png;base64'), ('jpeg', 'image/jpeg;base64'), ('html', 'HTML')], max_length=20)),
                ('content', Posts.models.Base64Field()),
                ('categories', models.CharField(choices=[('web', 'Web'), ('tutorial', 'Tutorial'), ('', '')], editable=False, max_length=20)),
                ('count', models.PositiveBigIntegerField(default=0)),
                ('size', models.PositiveBigIntegerField(default=10)),
                ('comments', models.CharField(default='', editable=False, max_length=200)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('visibility', models.CharField(max_length=20)),
                ('unlisted', models.BooleanField(default=False)),
                ('author_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('comment_pk', models.CharField(default='77fe1cd0934349be899bc2894c5266e0', editable=False, max_length=100, primary_key=True, serialize=False)),
                ('author', models.JSONField(editable=False)),
                ('id', models.CharField(editable=False, max_length=200)),
                ('type', models.CharField(default='comment', editable=False, max_length=30)),
                ('size', models.PositiveBigIntegerField(default=10)),
                ('contentType', models.CharField(choices=[('markdown', 'text/markdown'), ('plain', 'text/plain'), ('app', 'application/base64'), ('png', 'image/png;base64'), ('jpeg', 'image/jpeg;base64'), ('html', 'HTML')], editable=False, max_length=20)),
                ('content', Posts.commentModel.Base64Field()),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('Post_pk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Posts.post')),
            ],
        ),
    ]
