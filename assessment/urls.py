from django.urls import path
from .views import assign_quiz,assign_quiz_individual

urlpatterns = [
    path('assign-quiz/submit/', assign_quiz, name='assessment-dashboard'),
    path('assign-quiz-individual/submit/', assign_quiz_individual, name='assign_quiz'),
]