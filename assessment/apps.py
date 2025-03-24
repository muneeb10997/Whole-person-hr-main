from django.apps import AppConfig


class AssessmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'assessment'
    def ready(self):
        from django.urls import include, path

        from horilla.urls import urlpatterns

        urlpatterns.append(
            path("assessment/", include("assessment.urls")),
        )
        super().ready()



