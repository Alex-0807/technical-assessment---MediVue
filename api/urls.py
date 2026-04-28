from django.urls import include, path
from .views import AddPatientView, ReadingView, GetPatientView,DeletePatientView
urlpatterns = [
       path("readings/", ReadingView.as_view(), name="reading-ingestion"),
       path("add_patients/", AddPatientView.as_view(), name="patient-ingestion"),
       path("get_patients/<str:patient_id>/", GetPatientView.as_view(), name="get-patient"),
       path("delete_patients/<str:patient_id>/", DeletePatientView.as_view(), name="delete-patient"),
]