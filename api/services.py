from datetime import timezone

from api.models import AlertDeviceIssue, Patient, AlertGlucThresholdBreach, PatientSummary

def evaluate_glucose_reading(reading):
    patient = Patient.objects.filter(patient_id=reading.patient_id).first()
    if not patient:
        raise ValueError("Patient not found")
    glucose_value = reading.reading.get("glucose_mgdl")
    if glucose_value is None:
        raise ValueError("Glucose value not found in reading")
    if glucose_value < patient.low_threshold_glucose_mgdl:
        return "Low"
    elif glucose_value > patient.high_threshold_glucose_mgdl:
        return "High"
    else:
        return "Normal"
    
def alert_gluc_threshold_breach(reading, evaluation):
    AlertGlucThresholdBreach.objects.create(
        patient_id=reading.patient_id,
        device_id=reading.device_id,
        reading=reading.reading,
        evaluation=evaluation
    )
def alert_device_issue(reading, issue):
    AlertDeviceIssue.objects.create(
        device_id=reading.device_id,
        reading=reading.reading,
        issue=issue
    )

def create_patient_summary(patient_id, time_in_range_pct, readings):
    PatientSummary.objects.create(
        patient_id=patient_id,
        time_in_range_pct=time_in_range_pct,
        readings=[r.reading for r in readings],
        created_at=timezone.now()
    )
    
def calculate_time_in_range_pct(readings, low_threshold, high_threshold):
    if not readings:
        return 0.0
    in_range_count = sum(1 for r in readings if low_threshold <= r.reading.get("glucose_mgdl", 0) <= high_threshold)
    return (in_range_count / len(readings)) * 100