# -*- coding: utf-8 -*-
# Generated by Django 4.0.4 on 2022-05-10 21:41

from django.db import migrations, models
import django.utils.timezone
import fernet_fields.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Registrant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("registration", fernet_fields.fields.EncryptedTextField()),
                ("redacted_at", models.DateTimeField(default=None)),
                ("vr_completed_at", models.DateTimeField(default=None)),
                ("ab_completed_at", models.DateTimeField(default=None)),
                ("ab_permanent", models.BooleanField(default=None)),
                ("session_id", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("ref", models.CharField(max_length=255, null=True)),
                ("is_citizen", models.BooleanField(default=None)),
                ("is_eighteen", models.BooleanField(default=None)),
                ("dob_year", models.IntegerField()),
                ("party", models.CharField(max_length=255, null=True)),
                ("county", models.CharField(max_length=255, null=True)),
                ("lang", models.CharField(max_length=2, null=True)),
                (
                    "signed_at",
                    models.DateTimeField(
                        blank=True, default=django.utils.timezone.now, null=True
                    ),
                ),
                ("reg_lookup_complete", models.BooleanField(default=False)),
                ("addr_lookup_complete", models.BooleanField(default=False)),
                ("reg_found", models.BooleanField(default=None)),
                ("identification_found", models.BooleanField(default=None)),
                ("ab_identification_found", models.BooleanField(default=None)),
            ],
        ),
        migrations.AddIndex(
            model_name="registrant",
            index=models.Index(
                fields=["vr_completed_at"], name="ksvotes_reg_vr_comp_800cf1_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="registrant",
            index=models.Index(
                fields=["ab_completed_at"], name="ksvotes_reg_ab_comp_51e949_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="registrant",
            index=models.Index(
                fields=["created_at"], name="ksvotes_reg_created_08cae3_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="registrant",
            index=models.Index(
                fields=["updated_at"], name="ksvotes_reg_updated_b9f235_idx"
            ),
        ),
    ]