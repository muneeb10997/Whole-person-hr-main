# Generated by Django 4.2.11 on 2025-02-25 19:05

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('recruitment', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('duration_minutes', models.IntegerField(default=60)),
                ('passing_score', models.IntegerField(default=70, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('quiz_content', models.JSONField(blank=True, help_text='Stores LLM-generated quiz questions, options, and answers', null=True)),
            ],
            options={
                'verbose_name_plural': 'Quizzes',
            },
        ),
        migrations.CreateModel(
            name='QuizAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('quiz_status', models.CharField(choices=[('not_started', 'Not Started'), ('started', 'Started'), ('paused', 'Paused'), ('submitted', 'Submitted'), ('graded', 'Graded')], default='not_started', max_length=20)),
                ('score', models.FloatField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('last_attempt_date', models.DateTimeField(blank=True, null=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('passed', models.BooleanField(blank=True, null=True)),
                ('user_responses', models.JSONField(blank=True, help_text="Stores user's answers and progress for each question", null=True)),
                ('assigned_to_candidate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quiz_assignments', to='recruitment.candidate')),
            ],
            options={
                'ordering': ['-assigned_date'],
            },
        ),
    ]
