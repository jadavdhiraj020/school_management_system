# Generated by Django 5.1.5 on 2025-02-04 16:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Class",
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
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "permissions": [
                    ("can_view_class", "Can view class"),
                    ("can_edit_class", "Can edit class"),
                ],
            },
        ),
    ]
