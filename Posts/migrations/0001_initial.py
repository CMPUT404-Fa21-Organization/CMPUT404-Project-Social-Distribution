# Generated by Django 3.2.7 on 2021-11-24 18:19

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
                ('post_pk', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('author', models.JSONField(editable=False)),
                ('id', models.CharField(editable=False, max_length=200)),
                ('type', models.CharField(default='post', editable=False, max_length=30)),
                ('title', models.CharField(max_length=200)),
                ('source', models.CharField(blank=True, max_length=200)),
                ('origin', models.CharField(blank=True, max_length=200)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/app', 'application/base64'), ('image/png', 'image/png;base64'), ('image/jpeg', 'image/jpeg;base64'), ('HTML', 'HTML')], max_length=20)),
                ('content', Posts.models.Base64Field()),
                ('categories', models.CharField(choices=[('Web', 'Web'), ('Tutorial', 'Tutorial'), ('', '')], max_length=20)),
                ('count', models.PositiveBigIntegerField(default=0)),
                ('size', models.PositiveBigIntegerField(default=10)),
                ('comments', models.CharField(editable=False, max_length=200)),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('visibility', models.CharField(max_length=20)),
                ('unlisted', models.BooleanField(default=False)),
                ('author_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('comment_pk', models.CharField(editable=False, max_length=100, primary_key=True, serialize=False)),
                ('Post_pk_str', models.CharField(editable=False, max_length=300)),
                ('auth_pk_str', models.CharField(blank=True, editable=False, max_length=300, null=True)),
                ('author', models.JSONField(editable=False)),
                ('id', models.CharField(editable=False, max_length=200)),
                ('type', models.CharField(default='comment', editable=False, max_length=30)),
                ('size', models.PositiveBigIntegerField(default=10)),
                ('contentType', models.CharField(choices=[('text/markdown', 'text/markdown'), ('text/plain', 'text/plain'), ('application/app', 'application/base64'), ('image/png', 'image/png;base64'), ('image/jpeg', 'image/jpeg;base64'), ('HTML', 'HTML')], editable=False, max_length=20)),
                ('content', Posts.commentModel.Base64Field()),
                ('published', models.DateTimeField(auto_now_add=True)),
                ('Post_pk', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comment', to='Posts.post')),
            ],
        ),
    ]