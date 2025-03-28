"""
filters.py

This page is used to register filter for recruitment models

"""
import uuid
import django_filters
from django import forms
from base.filters import FilterSet
from recruitment.models import (
    Candidate,
    CandidateApplication,
    InterviewSchedule,
    Recruitment,
    RecruitmentSurvey,
    SkillZone,
    SkillZoneCandidate,
    Stage,
    SurveyTemplate,
)

# from django.forms.widgets import Boo



from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get dictionary item by key
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

import django_filters
from django import forms
from django_filters import FilterSet
from .models import Candidate, CandidateApplication

class CandidateFilter(FilterSet):
    """
    Filter set class for Candidate personal information
    """
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    mobile = django_filters.CharFilter(field_name="mobile", lookup_expr="icontains")
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")
    state = django_filters.CharFilter(field_name="state", lookup_expr="icontains")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")
    zip = django_filters.CharFilter(field_name="zip", lookup_expr="icontains")
    gender = django_filters.ChoiceFilter(field_name="gender", choices=Candidate.gender_choices)
    is_active = django_filters.BooleanFilter(field_name="is_active")
    
    class Meta:
        model = Candidate
        fields = [
            "name",
            "email",
            "mobile",
            "country",
            "state",
            "city",
            "zip",
            "gender",
            "is_active",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields["is_active"].initial = True
        for field in self.form.fields.keys():
            self.form.fields[field].widget.attrs["id"] = f"field_{field}"  # Using a simpler unique ID

class CandidateApplicationFilter(FilterSet):
    """
    Filter set class for CandidateApplication model
    """
    candidate_name = django_filters.CharFilter(field_name="candidate__name", lookup_expr="icontains")
    recruitment = django_filters.CharFilter(field_name="recruitment_id__title", lookup_expr="icontains")
    stage = django_filters.CharFilter(field_name="stage_id__stage", lookup_expr="icontains")
    schedule_date = django_filters.DateFilter(field_name="schedule_date", widget=forms.DateInput(attrs={"type": "date"}))
    interview_date = django_filters.DateFilter(field_name="interviews__interview_date", widget=forms.DateInput(attrs={"type": "date"}))
    scheduled_till = django_filters.DateFilter(field_name="interviews__interview_date", lookup_expr="lte", widget=forms.DateInput(attrs={"type": "date"}))
    scheduled_from = django_filters.DateFilter(field_name="interviews__interview_date", lookup_expr="gte", widget=forms.DateInput(attrs={"type": "date"}))
    probation_end = django_filters.DateFilter(field_name="probation_end", widget=forms.DateInput(attrs={"type": "date"}))
    probation_end_till = django_filters.DateFilter(field_name="probation_end", lookup_expr="lte", widget=forms.DateInput(attrs={"type": "date"}))
    probation_end_from = django_filters.DateFilter(field_name="probation_end", lookup_expr="gte", widget=forms.DateInput(attrs={"type": "date"}))
    offer_letter_status = django_filters.ChoiceFilter(field_name="offer_letter_status", choices=CandidateApplication.offer_letter_statuses)
    
    portal_sent = django_filters.BooleanFilter(field_name="onboarding_portal", method="filter_mail_sent", widget=django_filters.widgets.BooleanWidget())
    joining_set = django_filters.BooleanFilter(field_name="joining_date", method="filter_joining_set", widget=django_filters.widgets.BooleanWidget())

    def filter_mail_sent(self, queryset, name, value):
        """
        Custom filter to check if onboarding portal email was sent.
        """
        if value:
            return queryset.exclude(onboarding_portal__isnull=True)
        return queryset

    def filter_joining_set(self, queryset, name, value):
        """
        Custom filter to check if joining date is set.
        """
        if value:
            return queryset.exclude(joining_date__isnull=True)
        return queryset

    class Meta:
        model = CandidateApplication
        fields = [
            "candidate_id",
            "recruitment",
            "recruitment_id",
            "stage_id",
            "schedule_date",
            "start_onboard",
            "hired",
            "converted",
            "canceled",
            "is_active",
            "job_position_id",
            "recruitment_id__company_id",
            "recruitment_id__closed",
            "recruitment_id__is_active",
            "job_position_id__department_id",
            "recruitment_id__recruitment_managers",
            "stage_id__stage_managers",
            "stage_id__stage_type",
            "joining_date",
            "offer_letter_status",
            "portal_sent",
            "joining_set",
            
        ]

BOOLEAN_CHOICES = (
    ("", ""),
    ("false", "False"),
    ("true", "True"),
)


class RecruitmentFilter(FilterSet):
    """
    Filter set class for Recruitment model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    candidate_name = django_filters.CharFilter(
        field_name="title", method="pipeline_search"
    )
    search_onboarding = django_filters.CharFilter(
        field_name="title", method="onboarding_search"
    )
    description = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateFilter(
        field_name="start_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    end_date = django_filters.DateFilter(
        field_name="end_date", widget=forms.DateInput(attrs={"type": "date"})
    )
    start_from = django_filters.DateFilter(
        field_name="start_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    end_till = django_filters.DateFilter(
        field_name="end_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    search = django_filters.CharFilter(method="filter_by_name")
    is_active = django_filters.ChoiceFilter(
        choices=[
            (True, "Yes"),
            (False, "No"),
        ]
    )

    class Meta:
        """
        Meta class to add the additional info
        """

        model = Recruitment
        fields = [
            "recruitment_managers",
            "company_id",
            "title",
            "is_event_based",
            "start_date",
            "end_date",
            "closed",
            "is_active",
            "is_published",
            "job_position_id",
        ]

    def filter_by_name(self, queryset, _, value):
        """
        Filter queryset by first name or last name.
        """
        # Split the search value into first name and last name
        parts = value.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        job_queryset = queryset.filter(
            open_positions__job_position__icontains=value
        ) | queryset.filter(title__icontains=value)
        if first_name and last_name:
            queryset = queryset.filter(
                recruitment_managers__employee_first_name__icontains=first_name,
                recruitment_managers__employee_last_name__icontains=last_name,
            )
        elif first_name:
            queryset = queryset.filter(
                recruitment_managers__employee_first_name__icontains=first_name
            )
        elif last_name:
            queryset = queryset.filter(
                recruitment_managers__employee_last_name__icontains=last_name
            )

        queryset = queryset | job_queryset
        return queryset.distinct()

    def pipeline_search(self, queryset, _, value):
        """
        This method is used to search recruitment
        """
        queryset = (
            queryset.filter(title__icontains=value)
            | queryset.filter(stage_set__stage__icontains=value)
            | queryset.filter(candidate__name__icontains=value)
        )
        return queryset.distinct()

    def onboarding_search(self, queryset, _, value):
        """
        This method is used to search recruitment
        """
        queryset = (
            queryset.filter(title__icontains=value)
            | queryset.filter(onboarding_stage__stage_title__icontains=value)
            | queryset.filter(
                candidate__onboarding_stage__candidate_id__name__icontains=value
            )
        )
        return queryset.distinct()


class StageFilter(FilterSet):
    """
    Filter set class for Stage model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    search = django_filters.CharFilter(method="filter_by_name")
    candidate_name = django_filters.CharFilter(method="pipeline_search")

    class Meta:
        """
        Meta class to add the additional info
        """

        model = Stage
        fields = [
            "recruitment_id",
            "recruitment_id__job_position_id",
            "recruitment_id__job_position_id__department_id",
            "recruitment_id__company_id",
            "recruitment_id__recruitment_managers",
            "stage_managers",
            "stage_type",
        ]

    def filter_by_name(self, queryset, _, value):
        """
        Filter queryset by first name or last name.
        """
        # Split the search value into first name and last name
        parts = value.split()
        first_name = parts[0]
        last_name = " ".join(parts[1:]) if len(parts) > 1 else ""
        recruitment_query = queryset.filter(recruitment_id__title__icontains=value)
        # Filter the queryset by first name and last name
        stage_queryset = queryset.filter(stage__icontains=value)
        if first_name and last_name:
            queryset = queryset.filter(
                stage_managers__employee_first_name__icontains=first_name,
                stage_managers__employee_last_name__icontains=last_name,
            )
        elif first_name:
            queryset = queryset.filter(
                stage_managers__employee_first_name__icontains=first_name
            )
        elif last_name:
            queryset = queryset.filter(
                stage_managers__employee_last_name__icontains=last_name
            )

        queryset = queryset | stage_queryset | recruitment_query
        return queryset

    def pipeline_search(self, queryset, _, value):
        """
        This method is used to search recruitment
        """
        queryset = (
            queryset.filter(stage__icontains=value)
            | queryset.filter(candidate__name__icontains=value)
            | queryset.filter(recruitment_id__title__icontains=value)
        )
        return queryset.distinct()


class SurveyFilter(FilterSet):
    """
    SurveyFIlter
    """

    options = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Options",
        field_name="options",
    )

    question = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Question",
        field_name="question",
    )

    class Meta:
        """
        class Meta for additional options
        """

        model = RecruitmentSurvey
        fields = "__all__"
        exclude = [
            "sequence",
        ]


class SurveyTemplateFilter(django_filters.FilterSet):
    """
    SurveyTemplateFilter
    """

    question = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Title",
        field_name="title",
    )

    class Meta:
        model = SurveyTemplate
        fields = "__all__"


class CandidateReGroup:
    """
    Class to keep the field name for group by option
    """
    fields = [
        ("", "select"),
        ("candidate__name", "Candidate Name"),
        ("recruitment_id", "Recruitment"),
        ("job_position_id", "Job Position"),
        ("hired", "Hired"),
        ("candidate__country", "Country"),
        ("stage_id", "Stage"),
        ("joining_date", "Date Joining"),
        ("probation_end", "Probation End"),
        ("offer_letter_status", "Offer Letter Status"),
    ]

class SkillZoneFilter(FilterSet):
    """
    Skillzone Filter
    """
    search = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    candidate_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SkillZoneCandidate.objects.all(), method="filter_candidate_id"
    )
    recruitment_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Recruitment.objects.all(), method="filter_recruitment_id"
    )

    class Meta:
        model = SkillZone
        fields = ["is_active"]

    def filter_candidate_id(self, queryset, name, value):
        """
        Custom method to filter by candidate_id via related SkillZoneCandidates
        """
        return queryset.filter(skillzonecandidate__candidate_id__in=value)

    def filter_recruitment_id(self, queryset, name, value):
        """
        Custom method to filter by recruitment_id via related CandidateApplications
        """
        return queryset.filter(skillzonecandidate__candidate_id__applications__recruitment_id__in=value)


class SkillZoneCandFilter(FilterSet):
    """
    Skillzone Candidate Filter
    """
    search = django_filters.CharFilter(
        field_name="candidate_id__name",
        method="cand_search"
    )
    recruitment_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Recruitment.objects.all(), method="filter_recruitment_id"
    )

    class Meta:
        model = SkillZoneCandidate
        fields = [
            "is_active",
            "candidate_id",
            "candidate_id__email",
            "candidate_id__mobile",
            "candidate_id__country",
            "candidate_id__state",
            "candidate_id__city",
            "candidate_id__zip",
            "candidate_id__gender",
        ]
        exclude = ["reason", "objects"]

    def cand_search(self, queryset, _, value):
        """
        This method is used to include candidates when searching in the skill zone
        """
        return queryset.filter(candidate_id__name__icontains=value)

    def filter_recruitment_id(self, queryset, name, value):
        """
        Custom method to filter by recruitment_id
        """
        return queryset.filter(candidate_id__applications__recruitment_id__in=value)



class InterviewFilter(FilterSet):
    """
    Filter set class for Candidate model

    Args:
        FilterSet (class): custom filter set class to apply styling
    """

    search = django_filters.CharFilter(
        field_name="candidate_id__name", lookup_expr="icontains"
    )

    scheduled_from = django_filters.DateFilter(
        field_name="interview_date",
        lookup_expr="gte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    # schedule_date = django_filters.DateFilter(
    #     field_name="interview_date",
    #     widget=forms.DateInput(attrs={"type": "date"}),
    # )
    scheduled_till = django_filters.DateFilter(
        field_name="interview_date",
        lookup_expr="lte",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        """
        Meta class to add the additional info
        """

        model = InterviewSchedule
        fields = [
            "candidate_id",
            "employee_id",
            "interview_date",

        ]