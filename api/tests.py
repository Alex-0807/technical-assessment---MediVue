import types

from django.test import TestCase

from api.models import AlertDeviceIssue, AlertGlucThresholdBreach, Patient
from api.services import alert_device_issue, alert_gluc_threshold_breach, evaluate_glucose_reading


class PatientModelTest(TestCase):
    def test_create_and_retrieve(self):
        Patient.objects.create(patient_id="P001", low_threshold_glucose_mgdl=70.0, high_threshold_glucose_mgdl=180.0)
        patient = Patient.objects.get(patient_id="P001")
        self.assertEqual(patient.low_threshold_glucose_mgdl, 70.0)
        self.assertEqual(patient.high_threshold_glucose_mgdl, 180.0)

    def test_patient_id_must_be_unique(self):
        Patient.objects.create(patient_id="P001", low_threshold_glucose_mgdl=70.0, high_threshold_glucose_mgdl=180.0)
        with self.assertRaises(Exception):
            Patient.objects.create(patient_id="P001", low_threshold_glucose_mgdl=80.0, high_threshold_glucose_mgdl=160.0)

    def test_str_fields_stored_correctly(self):
        patient = Patient.objects.create(patient_id="P-XYZ", low_threshold_glucose_mgdl=65.5, high_threshold_glucose_mgdl=195.5)
        self.assertEqual(patient.patient_id, "P-XYZ")
        self.assertAlmostEqual(patient.low_threshold_glucose_mgdl, 65.5)
        self.assertAlmostEqual(patient.high_threshold_glucose_mgdl, 195.5)


def _make_reading(patient_id="P001", device_id="D001", glucose=100.0):
    return types.SimpleNamespace(
        patient_id=patient_id,
        device_id=device_id,
        reading={"glucose_mgdl": glucose},
    )


class EvaluateGlucoseReadingTest(TestCase):
    def setUp(self):
        Patient.objects.create(patient_id="P001", low_threshold_glucose_mgdl=70.0, high_threshold_glucose_mgdl=180.0)

    def test_normal_reading(self):
        self.assertEqual(evaluate_glucose_reading(_make_reading(glucose=100.0)), "Normal")

    def test_low_reading(self):
        self.assertEqual(evaluate_glucose_reading(_make_reading(glucose=50.0)), "Low")

    def test_high_reading(self):
        self.assertEqual(evaluate_glucose_reading(_make_reading(glucose=250.0)), "High")

    def test_exactly_at_low_threshold_is_normal(self):
        # boundary: strictly less-than triggers Low, equal is Normal
        self.assertEqual(evaluate_glucose_reading(_make_reading(glucose=70.0)), "Normal")

    def test_exactly_at_high_threshold_is_normal(self):
        # boundary: strictly greater-than triggers High, equal is Normal
        self.assertEqual(evaluate_glucose_reading(_make_reading(glucose=180.0)), "Normal")

    def test_patient_not_found_raises(self):
        reading = _make_reading(patient_id="DOES_NOT_EXIST")
        with self.assertRaises(ValueError) as ctx:
            evaluate_glucose_reading(reading)
        self.assertIn("Patient not found", str(ctx.exception))

    def test_missing_glucose_key_raises(self):
        reading = types.SimpleNamespace(patient_id="P001", device_id="D001", reading={"battery_pct": 80})
        with self.assertRaises(ValueError) as ctx:
            evaluate_glucose_reading(reading)
        self.assertIn("Glucose value not found", str(ctx.exception))


class AlertGlucThresholdBreachTest(TestCase):
    def setUp(self):
        self.reading = _make_reading(glucose=50.0)

    def test_creates_low_alert_record(self):
        alert_gluc_threshold_breach(self.reading, "Low")
        self.assertEqual(AlertGlucThresholdBreach.objects.count(), 1)
        alert = AlertGlucThresholdBreach.objects.first()
        self.assertEqual(alert.patient_id, "P001")
        self.assertEqual(alert.device_id, "D001")
        self.assertEqual(alert.evaluation, "Low")
        self.assertEqual(alert.reading, {"glucose_mgdl": 50.0})

    def test_creates_high_alert_record(self):
        reading = _make_reading(glucose=250.0)
        alert_gluc_threshold_breach(reading, "High")
        alert = AlertGlucThresholdBreach.objects.first()
        self.assertEqual(alert.evaluation, "High")

    def test_each_call_creates_a_new_record(self):
        alert_gluc_threshold_breach(self.reading, "Low")
        alert_gluc_threshold_breach(self.reading, "High")
        self.assertEqual(AlertGlucThresholdBreach.objects.count(), 2)


class AlertDeviceIssueTest(TestCase):
    def setUp(self):
        self.reading = types.SimpleNamespace(
            device_id="D001",
            reading={"glucose_mgdl": 100.0, "battery_pct": 10},
        )

    def test_creates_low_battery_alert(self):
        alert_device_issue(self.reading, "Low Battery")
        self.assertEqual(AlertDeviceIssue.objects.count(), 1)
        alert = AlertDeviceIssue.objects.first()
        self.assertEqual(alert.device_id, "D001")
        self.assertEqual(alert.issue, "Low Battery")
        self.assertEqual(alert.reading, {"glucose_mgdl": 100.0, "battery_pct": 10})

    def test_creates_poor_signal_alert(self):
        reading = types.SimpleNamespace(
            device_id="D001",
            reading={"glucose_mgdl": 100.0, "signal_quality": "poor"},
        )
        alert_device_issue(reading, "Poor Signal Quality")
        alert = AlertDeviceIssue.objects.first()
        self.assertEqual(alert.issue, "Poor Signal Quality")

    def test_each_call_creates_a_new_record(self):
        alert_device_issue(self.reading, "Low Battery")
        alert_device_issue(self.reading, "Poor Signal Quality")
        self.assertEqual(AlertDeviceIssue.objects.count(), 2)
