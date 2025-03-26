"""
models.py

This module is used to register models for recruitment app

"""

import json
import os
import re
from datetime import date
from uuid import uuid4

import django
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from base.horilla_company_manager import HorillaCompanyManager
from base.models import Company, JobPosition
from employee.models import Employee
from horilla.models import HorillaModel
from horilla_audit.methods import get_diff
from horilla_audit.models import HorillaAuditInfo, HorillaAuditLog
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from base.models import HorillaModel
# Create your models here.


def validate_mobile(value):
    """
    This method is used to validate the mobile number using regular expression
    """
    pattern = r"^\+[0-9 ]+$|^[0-9 ]+$"

    if re.match(pattern, value) is None:
        if "+" in value:
            raise forms.ValidationError(
                "Invalid input: Plus symbol (+) should only appear at the beginning \
                    or no other characters allowed."
            )
        raise forms.ValidationError(
            "Invalid input: Only digits and spaces are allowed."
        )


def validate_pdf(value):
    """
    This method is used to validate pdf
    """
    ext = os.path.splitext(value.name)[1]  # Get file extension
    if ext.lower() != ".pdf":
        raise ValidationError(_("File must be a PDF."))


def validate_image(value):
    """
    This method is used to validate the image
    """
    return value


def candidate_photo_upload_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{instance.name.replace(' ', '_')}_{filename}_{uuid4()}.{ext}"
    return os.path.join("recruitment/profile/", filename)


class SurveyTemplate(HorillaModel):
    """
    SurveyTemplate Model
    """

    title = models.CharField(max_length=30, unique=True)
    description = models.TextField(null=True, blank=True)
    is_general_template = models.BooleanField(default=False, editable=False)
    company_id = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    objects = HorillaCompanyManager("company_id")

    def __str__(self) -> str:
        return self.title


class Skill(HorillaModel):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        title = self.title
        self.title = title.capitalize()
        super().save(*args, **kwargs)


class Recruitment(HorillaModel):
    """
    Recruitment model
    """

    title = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True)
    is_event_based = models.BooleanField(
        default=False,
        help_text=_("To start recruitment for multiple job positions"),
    )
    closed = models.BooleanField(
        default=False,
        help_text=_(
            "To close the recruitment, If closed then not visible on pipeline view."
        ),
    )
    is_published = models.BooleanField(
        default=True,
        help_text=_(
            "To publish a recruitment in website, if false then it \
            will not appear on open recruitment page."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_(
            "To archive and un-archive a recruitment, if active is false then it \
            will not appear on recruitment list view."
        ),
    )
    open_positions = models.ManyToManyField(
        JobPosition, related_name="open_positions", blank=True
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_constraint=False,
        related_name="recruitment",
        verbose_name=_("Job Position"),
        editable=False,
    )
    vacancy = models.IntegerField(default=0, null=True)
    recruitment_managers = models.ManyToManyField(Employee)
    survey_templates = models.ManyToManyField(SurveyTemplate, blank=True)
    company_id = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    start_date = models.DateField(default=django.utils.timezone.now)
    end_date = models.DateField(blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    objects = HorillaCompanyManager()
    default = models.manager.Manager()
    optional_profile_image = models.BooleanField(
        default=False, help_text=_("Profile image not mandatory for candidate creation")
    )
    optional_resume = models.BooleanField(
        default=False, help_text=_("Resume not mandatory for candidate creation")
    )

    class Meta:
        """
        Meta class to add the additional info
        """

        unique_together = [
            (
                "job_position_id",
                "start_date",
            ),
            ("job_position_id", "start_date", "company_id"),
        ]
        permissions = (("archive_recruitment", "Archive Recruitment"),)

    def total_hires(self):
        """
        This method is used to get the count of
        hired candidates
        """
        return self.candidate.filter(hired=True).count()

    def __str__(self):
        title = (
            f"{self.job_position_id.job_position} {self.start_date}"
            if self.title is None and self.job_position_id
            else self.title
        )

        if not self.is_event_based and self.job_position_id is not None:
            self.open_positions.add(self.job_position_id)

        return title

    def clean(self):
        if self.title is None:
            raise ValidationError({"title": _("This field is required")})
        if self.is_published:
            if self.vacancy <= 0:
                raise ValidationError(
                    _(
                        "Vacancy must be greater than zero if the recruitment is publishing."
                    )
                )

        if self.end_date is not None and (
            self.start_date is not None and self.start_date > self.end_date
        ):
            raise ValidationError(
                {"end_date": _("End date cannot be less than start date.")}
            )
        return super().clean()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the Recruitment instance first
        if self.is_event_based and self.open_positions is None:
            raise ValidationError({"open_positions": _("This field is required")})

    def ordered_stages(self):
        """
        This method will returns all the stage respectively to the ascending order of stages
        """
        return self.stage_set.order_by("sequence")

    def is_vacancy_filled(self):
        """
        This method is used to check wether the vaccancy for the recruitment is completed or not
        """
        hired_stage = Stage.objects.filter(
            recruitment_id=self, stage_type="hired"
        ).first()
        if hired_stage:
            hired_candidate = hired_stage.candidate_set.all().exclude(canceled=True)
            if len(hired_candidate) >= self.vacancy:
                return True


@receiver(post_save, sender=Recruitment)
def create_initial_stage(sender, instance, created, **kwargs):
    """
    This is post save method, used to create initial stage for the recruitment
    """
    if created:
        applied_stage = Stage()
        applied_stage.sequence = 0
        applied_stage.recruitment_id = instance
        applied_stage.stage = "Applied"
        applied_stage.stage_type = "applied"
        applied_stage.save()

        initial_stage = Stage()
        initial_stage.sequence = 1
        initial_stage.recruitment_id = instance
        initial_stage.stage = "Initial"
        initial_stage.stage_type = "initial"
        initial_stage.save()


class Stage(HorillaModel):
    """
    Stage model
    """

    stage_types = [
        ("initial", _("Initial")),
        ("applied", _("Applied")),
        ("test", _("Test")),
        ("interview", _("Interview")),
        ("cancelled", _("Cancelled")),
        ("hired", _("Hired")),
    ]
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.CASCADE,
        related_name="stage_set",
        verbose_name=_("Recruitment"),
    )

    stage_managers = models.ManyToManyField(Employee)
    stage = models.CharField(max_length=50)
    stage_type = models.CharField(
        max_length=20, choices=stage_types, default="interview"
    )
    sequence = models.IntegerField(null=True, default=0)
    objects = HorillaCompanyManager(related_company_field="recruitment_id__company_id")

    def __str__(self):
        return f"{self.stage}"

    class Meta:
        """
        Meta class to add the additional info
        """

        permissions = (("archive_Stage", "Archive Stage"),)
        unique_together = ["recruitment_id", "stage"]
        ordering = ["sequence"]

    def active_candidates(self):
        """
        This method is used to get all the active candidate like related objects
        """
        return {
            "all": Candidate.objects.filter(
                stage_id=self, canceled=False, is_active=True
            )
        }


from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class Candidate(HorillaModel):
    """
    Candidate model (Personal details)
    """
    name = models.CharField(max_length=100, null=True, verbose_name=_("Name"))
    profile = models.ImageField(upload_to=candidate_photo_upload_path, null=True)
    email = models.EmailField(max_length=254, verbose_name=_("Email"))
    mobile = models.CharField(
        max_length=15,
        blank=True,
        validators=[validate_mobile],
        verbose_name=_("Phone"),
    )
    address = models.TextField(
        null=True, blank=True, verbose_name=_("Address"), max_length=255
    )
    country = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Country"))
    state = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("State"))
    city = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("City"))
    zip = models.CharField(max_length=30, null=True, blank=True, verbose_name=_("Zip Code"))
    dob = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    gender_choices = [("male", _( "Male")), ("female", _( "Female")), ("other", _( "Other"))]
    gender = models.CharField(
        max_length=15,
        choices=gender_choices,
        null=True,
        default="male",
        verbose_name=_("Gender"),
    )

    def __str__(self):
        return f"{self.name}"

    def get_full_name(self):
        return str(self.name)
    
    def get_avatar(self):
        url = f"https://ui-avatars.com/api/?name={self.get_full_name()}&background=random"
        if self.profile and default_storage.exists(self.profile.name):
            url = self.profile.url
        return url

    class Meta:
        ordering = ["name"]


class CandidateApplication(HorillaModel):
    """
    Candidate Application model (Job-related details)
    """
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.PROTECT,
        null=True,
        related_name="candidate_application",
        verbose_name=_("Recruitment"),
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_("Job Position"),
    )
    stage_id = models.ForeignKey(
        Stage,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_("Stage"),
    )
    converted_employee_id = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="candidate_get",
        verbose_name=_("Employee"),
    )
    schedule_date = models.DateTimeField(blank=True, null=True, verbose_name=_("Schedule date"))
    resume = models.FileField(
        upload_to="recruitment/resume",
        validators=[validate_pdf],
    )
    referral = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="candidate_referral",
        verbose_name=_("Referral"),
    )
    source_choices = [
        ("application", _( "Application Form")),
        ("software", _( "Inside software")),
        ("other", _( "Other")),
    ]
    source = models.CharField(
        max_length=20,
        choices=source_choices,
        null=True,
        blank=True,
        verbose_name=_("Source"),
    )
    start_onboard = models.BooleanField(default=False, verbose_name=_("Start Onboard"))
    hired = models.BooleanField(default=False, verbose_name=_("Hired"))
    canceled = models.BooleanField(default=False, verbose_name=_("Canceled"))
    converted = models.BooleanField(default=False, verbose_name=_("Converted"))
    joining_date = models.DateField(blank=True, null=True, verbose_name=_("Joining Date"))
    sequence = models.IntegerField(null=True, default=0)
    probation_end = models.DateField(null=True, editable=False)
    offer_letter_statuses = [
        ("not_sent", "Not Sent"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("joined", "Joined"),
    ]
    offer_letter_status = models.CharField(
        max_length=10,
        choices=offer_letter_statuses,
        default="not_sent",
        editable=False,
    )
    last_updated = models.DateField(null=True, auto_now=True)

    def save(self, *args, **kwargs):
        if self.stage_id and self.stage_id.stage_type == "hired":
            self.hired = True
        if self.stage_id and self.stage_id.stage_type == "cancelled":
            self.canceled = True
        if self.converted:
            self.hired = False
            self.canceled = False
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ["sequence"]



from horilla.signals import pre_bulk_update


class RejectReason(HorillaModel):
    """
    RejectReason
    """

    title = models.CharField(
        max_length=20,
    )
    description = models.TextField(null=True, blank=True, max_length=255)
    company_id = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Company"),
    )
    objects = HorillaCompanyManager()

    def __str__(self) -> str:
        return self.title


class RejectedCandidate(HorillaModel):
    """
    RejectedCandidate
    """

    candidate_id = models.OneToOneField(
        Candidate,
        on_delete=models.PROTECT,
        verbose_name="Candidate",
        related_name="rejected_candidate",
    )
    reject_reason_id = models.ManyToManyField(
        RejectReason, verbose_name="Reject reason", blank=True
    )
    description = models.TextField(max_length=255)
    objects = HorillaCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )
    history = HorillaAuditLog(
        related_name="history_set",
        bases=[
            HorillaAuditInfo,
        ],
    )

    def __str__(self) -> str:
        return super().__str__()


class StageFiles(HorillaModel):
    files = models.FileField(upload_to="recruitment/stageFiles", blank=True, null=True)

    def __str__(self):
        return self.files.name.split("/")[-1]


class StageNote(HorillaModel):
    """
    StageNote model
    """

    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    description = models.TextField(verbose_name=_("Description"), max_length=255)
    stage_id = models.ForeignKey(Stage, on_delete=models.CASCADE)
    stage_files = models.ManyToManyField(StageFiles, blank=True)
    updated_by = models.ForeignKey(
        Employee, on_delete=models.CASCADE, null=True, blank=True
    )
    candidate_can_view = models.BooleanField(default=False)
    objects = HorillaCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )

    def __str__(self) -> str:
        return f"{self.description}"

    def updated_user(self):
        if self.updated_by:
            return self.updated_by
        else:
            return self.candidate_id


class RecruitmentSurvey(HorillaModel):
    """
    RecruitmentSurvey model
    """

    question_types = [
        ("checkbox", _("Yes/No")),
        ("options", _("Choices")),
        ("multiple", _("Multiple Choice")),
        ("text", _("Text")),
        ("number", _("Number")),
        ("percentage", _("Percentage")),
        ("date", _("Date")),
        ("textarea", _("Textarea")),
        ("file", _("File Upload")),
        ("rating", _("Rating")),
    ]
    question = models.TextField(null=False, max_length=255)
    template_id = models.ManyToManyField(
        SurveyTemplate, verbose_name="Template", blank=True
    )
    is_mandatory = models.BooleanField(default=False)
    recruitment_ids = models.ManyToManyField(
        Recruitment,
        verbose_name=_("Recruitment"),
    )
    question = models.TextField(null=False)
    job_position_ids = models.ManyToManyField(
        JobPosition, verbose_name=_("Job Positions"), editable=False
    )
    sequence = models.IntegerField(null=True, default=0)
    type = models.CharField(
        max_length=15,
        choices=question_types,
    )
    options = models.TextField(
        null=True, default="", help_text=_("Separate choices by ',  '"), max_length=255
    )
    objects = HorillaCompanyManager(related_company_field="recruitment_ids__company_id")

    def __str__(self) -> str:
        return str(self.question)

    def choices(self):
        """
        Used to split the choices
        """
        return self.options.split(", ")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.template_id is None:
            general_template = SurveyTemplate.objects.filter(
                is_general_template=True
            ).first()
            if general_template:
                self.template_id.add(general_template)
                super().save(*args, **kwargs)

    class Meta:
        ordering = [
            "sequence",
        ]


class QuestionOrdering(HorillaModel):
    """
    Survey Template model
    """

    question_id = models.ForeignKey(RecruitmentSurvey, on_delete=models.CASCADE)
    recruitment_id = models.ForeignKey(Recruitment, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    objects = HorillaCompanyManager(related_company_field="recruitment_ids__company_id")


class RecruitmentSurveyAnswer(HorillaModel):
    """
    RecruitmentSurveyAnswer
    """

    candidate_id = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    recruitment_id = models.ForeignKey(
        Recruitment,
        on_delete=models.PROTECT,
        verbose_name=_("Recruitment"),
        null=True,
    )
    job_position_id = models.ForeignKey(
        JobPosition,
        on_delete=models.PROTECT,
        verbose_name=_("Job Position"),
        null=True,
    )
    answer_json = models.JSONField()
    attachment = models.FileField(
        upload_to="recruitment_attachment", null=True, blank=True
    )
    objects = HorillaCompanyManager(related_company_field="recruitment_id__company_id")

    @property
    def answer(self):
        """
        Used to convert the json to dict
        """
        # Convert the JSON data to a dictionary
        try:
            return json.loads(self.answer_json)
        except json.JSONDecodeError:
            return {}  # Return an empty dictionary if JSON is invalid or empty

    def __str__(self) -> str:
        return f"{self.candidate_id.name}-{self.recruitment_id}"


class RecruitmentMailTemplate(HorillaModel):
    title = models.CharField(max_length=25, unique=True)
    body = models.TextField()
    company_id = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )

    def __str__(self) -> str:
        return f"{self.title}"


class SkillZone(HorillaModel):
    """ "
    Model for talent pool
    """

    title = models.CharField(max_length=50, verbose_name="Skill Zone")
    description = models.TextField(verbose_name=_("Description"), max_length=255)
    company_id = models.ForeignKey(
        Company,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    objects = HorillaCompanyManager()

    def get_active(self):
        return SkillZoneCandidate.objects.filter(is_active=True, skill_zone_id=self)

    def __str__(self) -> str:
        return self.title


class SkillZoneCandidate(HorillaModel):
    """
    Model for saving candidate data's for future recruitment
    """

    skill_zone_id = models.ForeignKey(
        SkillZone,
        verbose_name=_("Skill Zone"),
        related_name="skillzonecandidate_set",
        on_delete=models.PROTECT,
        null=True,
    )
    candidate_id = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        null=True,
        related_name="skillzonecandidate_set",
        verbose_name=_("Candidate"),
    )
    # job_position_id=models.ForeignKey(
    #     JobPosition,
    #     on_delete=models.PROTECT,
    #     null=True,
    #     related_name="talent_pool",
    #     verbose_name=_("Job Position")
    # )

    reason = models.CharField(max_length=200, verbose_name=_("Reason"))
    added_on = models.DateField(auto_now_add=True)
    objects = HorillaCompanyManager(
        related_company_field="candidate_id__recruitment_id__company_id"
    )

    def clean(self):
        # Check for duplicate entries in the database
        duplicate_exists = (
            SkillZoneCandidate.objects.filter(
                candidate_id=self.candidate_id, skill_zone_id=self.skill_zone_id
            )
            .exclude(pk=self.pk)
            .exists()
        )

        if duplicate_exists:
            raise ValidationError(
                _(
                    f"Candidate {self.candidate_id} already exists in Skill Zone {self.skill_zone_id}."
                )
            )

        super().clean()

    def __str__(self) -> str:
        return str(self.candidate_id.get_full_name())


class CandidateRating(HorillaModel):
    employee_id = models.ForeignKey(
        Employee, on_delete=models.PROTECT, related_name="candidate_rating"
    )
    candidate_id = models.ForeignKey(
        Candidate, on_delete=models.PROTECT, related_name="candidate_rating"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ["employee_id", "candidate_id"]

    def __str__(self) -> str:
        return f"{self.employee_id} - {self.candidate_id} rating {self.rating}"


class RecruitmentGeneralSetting(HorillaModel):
    """
    RecruitmentGeneralSettings model
    """

    candidate_self_tracking = models.BooleanField(default=False)
    show_overall_rating = models.BooleanField(default=False)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)


class InterviewSchedule(HorillaModel):
    """
    Interview Scheduling Model
    """

    candidate_id = models.ForeignKey(
        Candidate,
        verbose_name=_("Candidate"),
        related_name="candidate_interview",
        on_delete=models.CASCADE,
    )
    employee_id = models.ManyToManyField(Employee, verbose_name=_("interviewer"))
    interview_date = models.DateField(verbose_name=_("Interview Date"))
    interview_time = models.TimeField(verbose_name=_("Interview Time"))
    description = models.TextField(
        verbose_name=_("Description"), blank=True, max_length=255
    )
    completed = models.BooleanField(
        default=False, verbose_name=_("Is Interview Completed")
    )
    objects = HorillaCompanyManager("candidate_id__recruitment_id__company_id")

    def __str__(self) -> str:
        return f"{self.candidate_id} -Interview."


class Resume(models.Model):
    file = models.FileField(
        upload_to="recruitment/resume",
        validators=[
            validate_pdf,
        ],
    )
    recruitment_id = models.ForeignKey(
        Recruitment, on_delete=models.CASCADE, related_name="resume"
    )
    is_candidate = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recruitment_id} - Resume {self.pk}"
    
     
STATUS = [
    ("requested", "Requested"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]

FORMATS = [
    ("any", "Any"),
    ("pdf", "PDF"),
    ("txt", "TXT"),
    ("docx", "DOCX"),
    ("xlsx", "XLSX"),
    ("jpg", "JPG"),
    ("png", "PNG"),
    ("jpeg", "JPEG"),
]


class CandidateDocumentRequest(HorillaModel):
    title = models.CharField(max_length=100)
    candidate_id = models.ManyToManyField(Candidate)
    format = models.CharField(choices=FORMATS, max_length=10)
    max_size = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=255)
    objects = HorillaCompanyManager(
        related_company_field="employee_id__employee_work_info__company_id"
    )

    def __str__(self):
        return self.title


class CandidateDocument(HorillaModel):
    title = models.CharField(max_length=250)
    candidate_id = models.ForeignKey(
        Candidate, on_delete=models.PROTECT, verbose_name="Candidate"
    )
    document_request_id = models.ForeignKey(
        CandidateDocumentRequest, on_delete=models.PROTECT, null=True
    )
    document = models.FileField(upload_to="candidate/documents", null=True)
    status = models.CharField(choices=STATUS, max_length=10, default="requested")
    reject_reason = models.TextField(blank=True, null=True, max_length=255)

    def __str__(self):
        return f"{self.candidate_id} - {self.title}"

    def clean(self, *args, **kwargs):
        super().clean(*args, **kwargs)
        file = self.document

        if len(self.title) < 3:
            raise ValidationError({"title": _("Title must be at least 3 characters")})

        if file and self.document_request_id:
            format = self.document_request_id.format
            max_size = self.document_request_id.max_size
            if max_size:
                if file.size > max_size * 1024 * 1024:
                    raise ValidationError(
                        {"document": _("File size exceeds the limit")}
                    )

            ext = file.name.split(".")[1].lower()
            if format == "any":
                pass
            elif ext != format:
                raise ValidationError(
                    {"document": _("Please upload {} file only.").format(format)}
                )


@receiver(m2m_changed, sender=CandidateDocumentRequest.candidate_id.through)
def document_request_m2m_changed(sender, instance, action, **kwargs):
    if action == "post_add":
        candidate_document_create(instance)

    elif action == "post_remove":
        candidate_document_create(instance)


def candidate_document_create(instance):
    candidates = instance.candidate_id.all()
    for candidate in candidates:
        document, created = CandidateDocument.objects.get_or_create(
            candidate_id=candidate,
            document_request_id=instance,
            defaults={"title": f"Upload {instance.title}"},
        )
        document.title = f"Upload {instance.title}"
        document.save()

class CandidateEvaluation(models.Model):
    """
    Model to store detailed breakdown of candidate evaluation scores
    """
    candidate = models.OneToOneField(
        'Candidate',
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='detailed_evaluation'
    )
    # Education and Experience
    education_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    experience_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Skills Impact
    soft_skills_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    technical_skills_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    composite_skills_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        editable=False
    )

    # Achievements Impact
    certifications_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    projects_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    awards_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    professional_presence_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    composite_achievements_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        editable=False
    )

    # Overall Impact
    overall_resume_impact = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        editable=False
    )
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_composite_scores(self):
        """
        Calculate composite scores based on individual impacts
        """
        # Calculate composite skills impact
        self.composite_skills_impact = round(
            0.30 * self.soft_skills_impact +
            0.70 * self.technical_skills_impact,
            2
        )

        # Calculate composite achievements impact
        self.composite_achievements_impact = round(
            0.30 * self.projects_impact +
            0.30 * self.certifications_impact +
            0.20 * self.awards_impact +
            0.20 * self.professional_presence_impact,
            2
        )

        # Calculate overall resume impact
        self.overall_resume_impact = round(
            0.25 * self.education_impact +
            0.30 * self.experience_impact +
            0.30 * self.composite_skills_impact +
            0.15 * self.composite_achievements_impact,
            2
        )

    def save(self, *args, **kwargs):
        self.calculate_composite_scores()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.candidate.id} Detailed Evaluation"



# class CandidateSkillAssessment(models.Model):
#     """
#     Model to track candidate's proficiency in specific skills
#     """
#     candidate = models.ForeignKey(
#         'Candidate',
#         on_delete=models.CASCADE,
#         related_name='skill_assessments'
#     )
#     skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
#     proficiency_level = models.ForeignKey(
#         SkillProficiencyLevel,
#         on_delete=models.SET_NULL,
#         null=True
#     )
#     assessment_date = models.DateTimeField(auto_now_add=True)
#     assessor = models.ForeignKey(
#         Employee,  # Now directly using the imported Employee model
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='conducted_assessments'
#     )
#     notes = models.TextField(blank=True)

#     class Meta:
#         unique_together = ['candidate', 'skill']
#         indexes = [
#             models.Index(fields=['candidate']),
#         ]

#     def __str__(self):
#         return f"{self.candidate.id} - {self.skill.title} Assessment"


class CandidateSkillAssessment(models.Model):
    """
    Model to store candidate's proficiency in specific skills
    """
    id = models.AutoField(primary_key=True)  # Primary key field
    candidate = models.ForeignKey(
        'Candidate',
        on_delete=models.CASCADE,
        related_name='skill_assessments'
    )
    skill_name = models.CharField(max_length=255)  # Skill name stored as a string
    proficiency_level = models.DecimalField(
        max_digits=4, decimal_places=2,  # Proficiency level (e.g., 0.00 to 99.99)
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ['candidate', 'skill_name']  # Ensure unique skills per candidate
        indexes = [
            models.Index(fields=['candidate']),  # Index for faster lookup by candidate
        ]

    def __str__(self):
        return f"Candidate {self.candidate.id} - Skill: {self.skill_name}, Proficiency: {self.proficiency_level}"



from django.contrib.postgres.fields import ArrayField

class CandidateMatchAnalysis(HorillaModel):
    """
    Model to store match analysis between candidates and job positions
    """
    id = models.AutoField(primary_key=True)

    # Use string references to avoid circular imports
    candidate = models.ForeignKey(
        'recruitment.Candidate',
        on_delete=models.CASCADE,
        related_name='match_analyses',
        verbose_name="Candidate"
    )

    job = models.ForeignKey(
        'base.JobPosition',
        on_delete=models.CASCADE,
        related_name='candidate_matches',
        verbose_name="Job Position"
    )

    match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Overall Match Score",
        help_text="Total match percentage between candidate and job"
    )

    skills_matched = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list,
        verbose_name="Matched Skills",
        help_text="List of skills that match with job requirements"
    )

    highest_qualification = models.CharField(
        max_length=255,
        verbose_name="Highest Qualification",
        help_text="Candidate's highest educational qualification"
    )

    experience_years = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0)],
        verbose_name="Years of Experience",
        help_text="Total work experience in years (e.g., 5.5 years)"
    )

    skills_match_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Skills Match Score",
        help_text="Percentage of required skills matched"
    )

    analysis_details = models.JSONField(
        default=dict,
        verbose_name="Analysis Details",
        help_text="Detailed analysis results in JSON format"
    )

    class Meta:
        verbose_name = "Candidate Match Analysis"
        verbose_name_plural = "Candidate Match Analyses"
        unique_together = ['candidate', 'job']
        indexes = [
            models.Index(fields=['candidate', 'job']),
            models.Index(fields=['match_score']),
            models.Index(fields=['skills_match_score']),
        ]

    def __str__(self):
        return f"Match Analysis - Candidate {self.candidate_id} for Job {self.job_id} - Score: {self.match_score}%"

    def save(self, *args, **kwargs):
        if not self.analysis_details:
            self.analysis_details = {
                'skill_breakdown': {},
                'experience_match': {
                    'relevant_years': float(self.experience_years),
                },
                'education_match': {
                    'degree': self.highest_qualification,
                }
            }
        super().save(*args, **kwargs)