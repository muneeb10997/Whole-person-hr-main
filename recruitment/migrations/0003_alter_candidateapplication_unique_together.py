# Generated by Django 4.2.11 on 2025-03-26 22:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recruitment', '0002_candidateapplication_alter_candidate_options_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='candidateapplication',
            unique_together=set(),
        ),
    ]
