# """
# assessments/sidebar.py

# To set WholepersonHR sidebar for assessments
# """

# from django.contrib.auth.context_processors import PermWrapper
# from django.urls import reverse
# from django.utils.translation import gettext_lazy as trans

# from recruitment.models import InterviewSchedule
# from recruitment.templatetags.recruitmentfilters import (
#     is_recruitmentmangers,
#     is_stagemanager,
# )

# MENU = trans("Assessments")
# ACCESSIBILITY = "recruitment.sidebar.menu_accessibilty"
# IMG_SRC = "images/ui/quiz_icon.svg"

# SUBMENUS = [
#     {
#         "menu": trans("Dashboard"),
#         "redirect": reverse("assessment-dashboard"),
#     },
# ]
"""
recruitment/sidebar.py

To set WholepersonHR sidebar for onboarding
"""


from django.urls import reverse
from django.utils.translation import gettext_lazy as trans



MENU = trans("Assessment")
IMG_SRC = "images/ui/quiz_icon.svg"

SUBMENUS = [
    {
        "menu": trans("Dashboard"),
        "redirect": reverse("assessment-dashboard"),
    }
]



