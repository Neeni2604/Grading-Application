# Generated by Django 5.1 on 2024-10-21 20:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0004_alter_submission_author_alter_submission_grader'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='points',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='weight',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='submission',
            name='grader',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='graded_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
