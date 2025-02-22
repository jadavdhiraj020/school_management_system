# Generated by Django 5.1.5 on 2025-02-04 16:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("school_class", "0001_initial"),
        ("subjects", "0001_initial"),
        ("teachers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="class",
            name="class_teacher",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="managed_classes",
                to="teachers.teacher",
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="subjects",
            field=models.ManyToManyField(
                related_name="classes",
                through="subjects.ClassTeacherSubject",
                to="subjects.subject",
            ),
        ),
        migrations.AddField(
            model_name="class",
            name="teachers",
            field=models.ManyToManyField(
                related_name="teaching_classes",
                through="subjects.ClassTeacherSubject",
                to="teachers.teacher",
            ),
        ),
        migrations.AddConstraint(
            model_name="class",
            constraint=models.UniqueConstraint(
                fields=("name",), name="unique_class_name"
            ),
        ),
    ]
