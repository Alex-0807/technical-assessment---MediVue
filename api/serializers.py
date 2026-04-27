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