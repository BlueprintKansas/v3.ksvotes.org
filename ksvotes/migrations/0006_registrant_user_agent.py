# -*- coding: utf-8 -*-
# Generated by Django 4.0.4 on 2022-07-29 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ksvotes", "0005_alter_registrant_options_remove_zipcode_counties_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="registrant",
            name="user_agent",
            field=models.CharField(max_length=255, null=True),
        ),
    ]
