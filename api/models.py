from django.db import models

# Create your models here.

status_choices = [
    ("active", "Active"),
    ("acknowledged", "Acknowledged"),
    ("supressed", "Suppressed"),
    ("resolved", "Resolved"),
    ("escalated", "Escalated"),
]
class Patient(models.Model):
    patient_id = models.CharField(max_length=255, unique=True)
    low_threshold_glucose_mgdl = models.FloatField()
    high_threshold_glucose_mgdl = models.FloatField()
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    assigned_doctor = models.CharField(max_length=255, null=True, blank=True)
    
class PatientMeducalHistory(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="medical_histories")
    condition = models.CharField(max_length=255)
    diagnosis_date = models.DateField()
    notes = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)
    genetic_diseases = models.TextField(null=True, blank=True)
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
    status = models.CharField(max_length=20, choices=status_choices, default="active")
class AlertDeviceIssue(models.Model):
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    issue=models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=status_choices, default="active")

class AlertHeartRateThresholdBreach(models.Model):
    patient_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    evaluation = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=status_choices, default="active")

class AlertBloodPressureThresholdBreach(models.Model):
    patient_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    evaluation = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=status_choices, default="active")

class AlertBloodOxygenThresholdBreach(models.Model):
    patient_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    evaluation = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=status_choices, default="active")
class AlertTemperatureThresholdBreach(models.Model):
    patient_id = models.CharField(max_length=255)
    device_id = models.CharField(max_length=255)
    reading = models.JSONField()
    evaluation = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=status_choices, default="active")

class PatientSummary(models.Model):
    patient_id = models.CharField(max_length=255, unique=True)
    time_in_range_pct = models.FloatField()
    readings = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
