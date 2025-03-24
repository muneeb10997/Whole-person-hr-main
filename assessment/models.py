from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from employee.models import Employee
from recruitment.models import Candidate, Recruitment
from django.utils import timezone



class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=60)
    passing_score = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Field to store LLM-generated quiz content
    quiz_content = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores LLM-generated quiz questions, options, and answers"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Quizzes"

class QuizAssignment(models.Model):
    ASSIGNMENT_STATUS = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired')
    )

    QUIZ_STATUS = (
        ('not_started', 'Not Started'),
        ('started', 'Started'),
        ('paused', 'Paused'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded')
    )

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assignments')
    assigned_to_employee = models.ForeignKey(
        Employee,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='quiz_assignments'
    )
    assigned_to_candidate = models.ForeignKey(
        Candidate,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='quiz_assignments'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS, default='pending')
    quiz_status = models.CharField(max_length=20, choices=QUIZ_STATUS, default='not_started')

    # Quiz scoring fields
    score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    passed = models.BooleanField(null=True, blank=True)

    # Field to store user's answers and progress
    user_responses = models.JSONField(
        null=True,
        blank=True,
        help_text="Stores user's answers and progress for each question"
    )

    class Meta:
        ordering = ['-assigned_date']

    def __str__(self):
        assignee = self.assigned_to_employee or self.assigned_to_candidate
        return f"{self.quiz.title} - {assignee}"

    def save(self, *args, **kwargs):
        if self.score is not None:
            self.passed = self.score >= self.quiz.passing_score

        if self.status == 'completed' and not self.completion_date:
            self.completion_date = timezone.now()

        if self.due_date and timezone.now() > self.due_date and self.status != 'completed':
            self.status = 'expired'

        super().save(*args, **kwargs)