from django.db import models

# Create your models here.
class Patient(models.Model):
    patient_id = models.CharField(max_length=255, unique=True)
    low_threshold_glucose_mgdl = models.FloatField()
    high_threshold_glucose_mgdl = models.FloatField()
class Reading(models.Model):
    device_id = models.CharField(max_length=255)
    patient_id = models.CharField(max_length=255)
    reading = models.JSONField()

class ReadingDeDupKey(models.Model):
    ReadingDeDupKey = models.CharField(max_length=255, unique=True)

class AlertGlucThresholdBreach(models.Model):
    patient_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    evaluation = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
class AlertDeviceIssue(models.Model):
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    issue=models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)