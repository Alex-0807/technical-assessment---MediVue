from rest_framework import serializers

class ReadingSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    patient_id = serializers.CharField()
    reading = serializers.JSONField()
    

class ReadingDataSerializer(serializers.Serializer):
    glucose_mgdl = serializers.FloatField()
    battery_pct = serializers.IntegerField()
    signal_quality = serializers.ChoiceField(choices=["good", "poor", "degraded"])
    recorded_at = serializers.DateTimeField()

class PatientSerializer(serializers.Serializer):
    patient_id = serializers.CharField()
    low_threshold_glucose_mgdl = serializers.FloatField()
    high_threshold_glucose_mgdl = serializers.FloatField()

class AlertGlucThresholdBreachSerializer(serializers.Serializer):
    patient_id = serializers.CharField()
    device_id = serializers.CharField()
    reading = serializers.JSONField()
    evaluation = serializers.CharField()

class AlertDeviceIssueSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    reading = serializers.JSONField()
    issue = serializers.CharField()
class PatientSummarySerializer(serializers.Serializer):
    patient_id = serializers.CharField()
    time_in_range_pct = serializers.FloatField()
    readings = serializers.JSONField()  
    created_at = serializers.DateTimeField()