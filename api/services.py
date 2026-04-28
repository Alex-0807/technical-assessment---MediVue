from api.models import AlertDeviceIssue, Patient, AlertGlucThresholdBreach

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