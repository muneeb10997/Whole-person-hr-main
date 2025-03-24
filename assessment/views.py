# views.py
from datetime import time
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import requests
from assessment.models import QuizAssignment
from horilla import settings
from recruitment.models import Candidate, Recruitment
from employee.models import Employee
from django.shortcuts import render, redirect
from django.contrib import messages
import requests
from .models import QuizAssignment, Quiz
from recruitment.models import Candidate, Recruitment
from employee.models import Employee
from django.db.models import Q
# Your existing skills dictionary



SKILLS = {
    "Programming": {
        "Python": ["Basic Python", "OOP", "Django", "FastAPI"],
        "JavaScript": ["ES6", "React", "Node.js", "Vue.js"],
        "Database": ["SQL", "MongoDB", "PostgreSQL"]
    },
    "Soft Skills": {
        "Communication": ["Written", "Verbal", "Presentation"],
        "Leadership": ["Team Management", "Decision Making", "Conflict Resolution"],
        "Problem Solving": ["Analytical Thinking", "Critical Thinking"]
    },
    "Domain Knowledge": {
        "HR": ["Recruitment", "Employee Relations", "Performance Management"],
        "Finance": ["Accounting", "Budgeting", "Financial Analysis"],
        "Marketing": ["Digital Marketing", "Content Strategy", "Brand Management"]
    }
}


# def assign_quiz(request):
#     """
#     View for assigning quizzes to candidates or employees with proper recruitment filtering
#     """
#     if request.method == 'POST':
#         assignee_candidate_ids = request.POST.getlist('assignee_candidate_ids[]')
#         canidate_id=request.POST.get('candidate_ids')
#         print("here is the canidate_id ",canidate_id)
#         if assignee_candidate_ids is []:
#                    assignee_candidate_ids = request.POST.getlist('candidate_ids')
#                    print("here is the", assignee_candidate_ids)
#         assignee_employee_ids = request.POST.getlist('assignee_employee_ids[]')
#         selected_skills = request.POST.getlist('skills[]')
#         print("here is selected skills ",selected_skills)

#         if not selected_skills and (not assignee_candidate_ids or not assignee_employee_ids):
#             messages.error(request, 'Please select skills')
#             return redirect('assessment-dashboard')
#         try:
#             # Process assignments
#                 if assignee_candidate_ids:
#                     print(assignee_candidate_ids)
#                     # Your quiz assignment logic for candidate
#                 else:
#                     print("here is employes ",   assignee_employee_ids)
#                     # Your quiz assignment logic for employee
#                 try:
#                         # Prepare the API request data
#                         api_data = {
#                             'candidates_ids': assignee_candidate_ids,
#                             'employee_ids' : assignee_employee_ids,
#                             'skills': selected_skills,
#                         }
#                         print("make calls ")
#                         api_url= f'{settings.RESUME_ASSESSMENT_API_URL}assign_quiz_by_admin'
#                         print("make calls ",api_url)
#                         # Make the API call
#                         response = requests.post(
#                             api_url,  # Add this URL to your settings
#                             json=api_data,
#                             headers={
#                                 'Content-Type': 'application/json'
#                             }
#                         )
#                         print("response")
#                         print(response.content)
#                         messages.success(request, f'Quiz successfully assigned to  people')
#                 except Exception as e:
#                     # Log the error but don't prevent the application from being saved
#                     print(f"Assessment Assign  processing error: {str(e)}")
#                 return redirect('assessment-dashboard')

#         except Exception as e:
#             messages.error(request, f'Error assigning quiz: {str(e)}')
#             return redirect('assessment-dashboard')
#     recruitment_id = request.GET.get("recruitment")

#     # Get all active recruitments for filter
#     recruitments = Recruitment.objects.filter(closed=False, is_active=True)

#     # Get active candidates with recruitment information
#     candidates = Candidate.objects.filter(
#         is_active=True
#     ).select_related('recruitment_id', 'job_position_id')

#     # Filter candidates by recruitment if specified
#     if recruitment_id:
#         candidates = candidates.filter(recruitment_id=recruitment_id)

#     # Get active employees
#     employees = Employee.objects.filter(is_active=True)

#     context = {
#         "candidates": candidates,
#         "employees": employees,
#         "recruitments": recruitments,
#         "skills": SKILLS,
#     }

#     return render(request, "assign_quiz.html", context)



def assign_quiz(request):
    """
    View for assigning quizzes to candidates/employees and viewing quiz results
    """
    # Handle quiz assignment POST request
    if request.method == 'POST':
        assignee_candidate_ids = request.POST.getlist('assignee_candidate_ids[]')
        deadline_date=request.POST.get('quiz_deadline_date')
        print("here is the date ",deadline_date)
        deadline_time=request.POST.get('quiz_deadline_time')

        if assignee_candidate_ids == []:
            assignee_candidate_ids = request.POST.getlist('candidate_ids')

        assignee_employee_ids = request.POST.getlist('assignee_employee_ids[]')
        selected_skills = request.POST.getlist('skills[]')

        if not selected_skills and (not assignee_candidate_ids or not assignee_employee_ids):
            messages.error(request, 'Please select skills')
            return redirect('assessment-dashboard')

        try:
            # Prepare the API request data
            api_data = {
                'candidates_ids': assignee_candidate_ids,
                'employee_ids': assignee_employee_ids,
                'skills': selected_skills,
                'deadline_date':deadline_date,
                'deadline_time':deadline_time
            }
            # Make the API call
            api_url = f'{settings.RESUME_ASSESSMENT_API_URL}assign_quiz_by_admin'
            response = requests.post(
                api_url,
                json=api_data,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                messages.success(request, 'Quiz successfully assigned')
            else:
                messages.error(request, 'Error assigning quiz: API call failed')

        except Exception as e:
            messages.error(request, f'Error assigning quiz: {str(e)}')
            print(f"Assessment Assign processing error: {str(e)}")

        return redirect('assessment-dashboard')
    assigned_candidate_ids = set()
    assigned_employee_ids = set()

    # Handle GET request for viewing assignments and results
    recruitment_id = request.GET.get("recruitment")
    view_results = request.GET.get("view_results", True)
    status_filter = request.GET.get("status")

    # Get all active recruitments for filter
    recruitments = Recruitment.objects.filter(closed=False, is_active=True)

    # Get active candidates with recruitment information
    candidates = Candidate.objects.filter(
        is_active=True
    ).select_related('recruitment_id', 'job_position_id')

    # Filter candidates by recruitment if specified
    if recruitment_id:
        candidates = candidates.filter(recruitment_id=recruitment_id)
        recruitment = Recruitment.objects.get(pk=recruitment_id, closed=False, is_active=True)


    # Get active employees
    employees = Employee.objects.filter(is_active=True)

    # Get quiz assignments and results if viewing results
    quiz_assignments = None
    if view_results:
        quiz_assignments = QuizAssignment.objects.filter(
            Q(assigned_to_candidate__isnull=False) |
            Q(assigned_to_employee__isnull=False)
        ).select_related(
            'quiz',
            'assigned_to_candidate',
            'assigned_to_employee',
            'assigned_to_candidate__recruitment_id',
            'assigned_to_candidate__job_position_id'
        )
        # Apply filters
        if recruitment_id:
            quiz_assignments = quiz_assignments.filter(
                assigned_to_candidate__recruitment_id=recruitment_id
            )

        if status_filter:
            quiz_assignments = quiz_assignments.filter(status=status_filter)

    all_assignments = QuizAssignment.objects.values_list(
        'assigned_to_candidate_id', 'assigned_to_employee_id'
    )
    for candidate_id, employee_id in all_assignments:
        if candidate_id:
            assigned_candidate_ids.add(candidate_id)
        if employee_id:
            assigned_employee_ids.add(employee_id)

    context = {
        "candidates": candidates,
        "employees": employees,
        "recruitments": recruitments,
        "skills": SKILLS,
        "quiz_assignments": quiz_assignments,
        "view_results": view_results,
        "selected_recruitment": recruitment_id,
        "selected_status": status_filter,
        "assigned_candidate_ids": assigned_candidate_ids,
        "assigned_employee_ids": assigned_employee_ids
    }

    template = "assign_quiz.html"
    return render(request, template, context)




# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.db.models import Q
# from .models import QuizAssignment, Quiz
# from recruitment.models import Candidate

# def quiz_results_dashboard(request):
#     """
#     View for HR to see completed quiz results for candidates
#     """
#     # Get filter parameters from request
#     recruitment_id = request.GET.get('recruitment')
#     quiz_id = request.GET.get('quiz')
#     status = request.GET.get('status', 'completed')  # Default to showing completed
#     passing_filter = request.GET.get('passing')

#     # Base queryset for completed quizzes
#     quiz_assignments = QuizAssignment.objects.filter(
#         assigned_to_candidate__isnull=False  # Only get candidate assignments
#     ).select_related(
#         'quiz',
#         'assigned_to_candidate',
#         'assigned_to_candidate__recruitment_id',
#         'assigned_to_candidate__job_position_id'
#     )

#     # Apply filters
#     if status:
#         quiz_assignments = quiz_assignments.filter(status=status)

#     if recruitment_id:
#         quiz_assignments = quiz_assignments.filter(
#             assigned_to_candidate__recruitment_id=recruitment_id
#         )

#     if quiz_id:
#         quiz_assignments = quiz_assignments.filter(quiz_id=quiz_id)

#     if passing_filter:
#         if passing_filter == 'passed':
#             quiz_assignments = quiz_assignments.filter(passed=True)
#         elif passing_filter == 'failed':
#             quiz_assignments = quiz_assignments.filter(passed=False)

#     # Get filter options for template
#     all_quizzes = Quiz.objects.all()
#     all_recruitments = Recruitment.objects.filter(closed=False, is_active=True)

#     context = {
#         'quiz_assignments': quiz_assignments,
#         'all_quizzes': all_quizzes,
#         'all_recruitments': all_recruitments,
#         'selected_recruitment': recruitment_id,
#         'selected_quiz': quiz_id,
#         'selected_status': status,
#         'selected_passing': passing_filter,
#     }

#     return render(request, 'quiz_results_dashboard.html', context)







def assign_quiz_individual(request):
    """
    View for assigning quizzes to candidates or employees with proper recruitment filtering
    """
    if request.method == 'POST':
        assignee_candidate_id=request.POST.get('candidate_ids')
        deadline_date=request.POST.get('quiz_deadline_date')
        print("here is the date ",deadline_date)
        deadline_time=request.POST.get('quiz_deadline_time')
        print(assignee_candidate_id)
        data_list = [int(x) for x in assignee_candidate_id.split(',')]
        selected_skills = request.POST.getlist('skills[]')
        print("here is selected skills ",selected_skills)

        if not selected_skills and not data_list:
            messages.error(request, 'Please select skills')
            return redirect('candidate-view')
        try:
            # Process assignments
                if data_list:
                    print(data_list)
                try:
                        # Prepare the API request data
                        api_data = {
                            'candidates_ids': data_list,
                            'skills': selected_skills,
                            'deadline_date':deadline_date,
                            'deadline_time':deadline_time
                        }
                        print("make calls ")
                        api_url= f'{settings.RESUME_ASSESSMENT_API_URL}assign_quiz_by_admin'
                        print("make calls ",api_url)
                        # Make the API call
                        response = requests.post(
                            api_url,  # Add this URL to your settings
                            json=api_data,
                            headers={
                                'Content-Type': 'application/json'
                            }
                        )
                        print("response")
                        print(response.content)
                        messages.success(request, f'Quiz successfully assigned to  candidates')
                except Exception as e:
                    # Log the error but don't prevent the application from being saved
                    print(f"Assessment Assign  processing error: {str(e)}")
                return redirect('candidate-view',messages="Quiz successfully assigned to  candidates")

        except Exception as e:
            messages.error(request, f'Error assigning quiz: {str(e)}')
            return redirect('candidate-view')


