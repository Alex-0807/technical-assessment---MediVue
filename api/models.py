from django.db import models

# Create your models here.
class Reading(models.Model):
    device_id = models.CharField(max_length=255)
    patient_id = models.CharField(max_length=255)
    reading = models.JSONField()

class ReadingDeDupKey(models.Model):
    ReadingDeDupKey = models.CharField(max_length=255, unique=True)
