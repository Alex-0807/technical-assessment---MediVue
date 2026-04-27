from django.urls import include, path
from .views import ReadingView

urlpatterns = [
       path("readings/", ReadingView.as_view(), name="reading-ingestion"),
]