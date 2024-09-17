# Generated by Django 5.1.1 on 2024-09-13 13:49

import base.models.item_models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.CharField(default=base.models.item_models.create_id, max_length=22, primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, default='anonymous', max_length=50, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('name', models.CharField(blank=True, default='', max_length=50)),
                ('zipcode', models.CharField(blank=True, default='', max_length=8)),
                ('prefecture', models.CharField(blank=True, default='', max_length=50)),
                ('city', models.CharField(blank=True, default='', max_length=50)),
                ('address1', models.CharField(blank=True, default='', max_length=50)),
                ('address2', models.CharField(blank=True, default='', max_length=50)),
                ('tel', models.CharField(blank=True, default='', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.CharField(default=base.models.item_models.create_id, editable=False, max_length=22, primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('price', models.PositiveIntegerField(default=0)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('description', models.TextField(blank=True, default='')),
                ('sold_count', models.PositiveIntegerField(default=0)),
                ('is_published', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('image', models.ImageField(blank=True, default='', upload_to=base.models.item_models.upload_image_to)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.category')),
                ('tags', models.ManyToManyField(to='base.tag')),
            ],
        ),
    ]
