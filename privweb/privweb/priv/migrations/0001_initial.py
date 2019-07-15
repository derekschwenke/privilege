# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-09 20:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission_name', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role_name', models.CharField(max_length=80)),
                ('permissions', models.ManyToManyField(to='priv.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acctname', models.CharField(max_length=24)),
                ('first_name', models.CharField(max_length=24)),
                ('last_name', models.CharField(max_length=24)),
            ],
        ),
        migrations.AddField(
            model_name='role',
            name='users',
            field=models.ManyToManyField(to='priv.User'),
        ),
    ]