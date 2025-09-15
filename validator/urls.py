from django.urls import path
from .views import SubmitValidationView, GetResultsView

urlpatterns = [
    path("validate-emails/", SubmitValidationView.as_view(), name="validate_emails"),
    path("results/", GetResultsView.as_view(), name="results"),
]
