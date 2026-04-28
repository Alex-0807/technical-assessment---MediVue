from datetime import timedelta, timezone

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status
from api.models import Reading, ReadingDeDupKey, Patient
from api.serializers import PatientSerializer, ReadingSerializer
from api.services import alert_device_issue, alert_gluc_threshold_breach, evaluate_glucose_reading
# Create your views here.

class ReadingView(APIView):
    def post(self, request):
        serializer = ReadingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        try:
            evaluation = evaluate_glucose_reading(**serializer.validated_data)
            if evaluation in ["Low", "High"]:
                alert_gluc_threshold_breach(**serializer.validated_data, evaluation=evaluation)
            else:
                print(f"Evaluation result: {evaluation}")
        except ValueError as e:
            evaluation = str(e)

        try:
            battery_pct= serializer.validated_data['reading'].get('battery_pct')
            signal_quality = serializer.validated_data['reading'].get('signal_quality')
            if battery_pct is not None and battery_pct < 20:
                evaluation = "Low Battery"
            elif signal_quality is not None and signal_quality in ["poor", "degraded"]:
                evaluation = "Poor Signal Quality"
            if evaluation in ["Low Battery", "Poor Signal Quality"]:
                alert_device_issue(**serializer.validated_data, issue=evaluation)
                
        except Exception as e:
            print(f"Error evaluating battery or signal quality: {e}")

        dedupKey = f"{serializer.validated_data['device_id']}_{serializer.validated_data['patient_id']}_{serializer.validated_data['reading'].get('recorded_at')}"
        if not ReadingDeDupKey.objects.filter(ReadingDeDupKey=dedupKey).exists():
        
            Reading.objects.create(**serializer.validated_data)
            ReadingDeDupKey.objects.create(ReadingDeDupKey=dedupKey)
            
            return Response({**serializer.data, "evaluation": evaluation}, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Duplicate reading"}, status=status.HTTP_409_CONFLICT)
        
    def get(self, request):
        readings = Reading.objects.all()
        return Response([{
            "device_id": reading.device_id,
            "patient_id": reading.patient_id,
            "reading": reading.reading,
            "evaluation": evaluate_glucose_reading(reading)
        } for reading in readings], status=status.HTTP_200_OK)

    
class AddPatientView(APIView):
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        Patient.objects.create(**serializer.validated_data)
        return Response({"detail": "Patient added successfully"}, status=status.HTTP_201_CREATED)

class GetPatientView(APIView):
    def get(self, request, patient_id):
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            serializer = PatientSerializer(patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
class DeletePatientView(APIView):
    def delete(self, request, patient_id):
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            patient.delete()
            return Response({"detail": "Patient deleted successfully"}, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        
class GetPatientSummaryView(APIView):
    def get(self, request, patient_id):
        try:
            n = int(request.query_params.get("n", 12))
            if not (1 <= n <= 200):
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "Bad Request", "message": "n must be an integer between 1 and 200"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


        try:
            cutoff      = timezone.now() - timedelta(hours=24)
            patient = Patient.objects.get(patient_id=patient_id)
            readings = (
                    Reading.objects
                    .filter(patient_id=patient_id, reading__recorded_at__gte=cutoff)
                    .order_by(F('reading__recorded_at').desc())
                    [:n]
                )
            serializer = PatientSerializer(patient)
            return Response({
                "patient": serializer.data,
                "readings": [{
                    "device_id": reading.device_id,
                    "reading": reading.reading,
                    "evaluation": evaluate_glucose_reading(reading)
                } for reading in readings]
            }, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)