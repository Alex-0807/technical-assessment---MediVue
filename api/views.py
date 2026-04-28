from datetime import timedelta, timezone

from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status
from api.models import PatientSummary, Reading, ReadingDeDupKey, Patient
from api.serializers import PatientSerializer, ReadingSerializer
from api.services import alert_device_issue, alert_gluc_threshold_breach, evaluate_glucose_reading, calculate_time_in_range_pct
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
            return Response({"detail": f"Error evaluating battery or signal quality: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        dedupKey = f"{serializer.validated_data['device_id']}_{serializer.validated_data['patient_id']}_{serializer.validated_data['reading'].get('recorded_at').replace(microsecond=0)}"
        if not ReadingDeDupKey.objects.filter(ReadingDeDupKey=dedupKey).exists():
        
            Reading.objects.create(**serializer.validated_data)
            ReadingDeDupKey.objects.create(ReadingDeDupKey=dedupKey)
            
            # this try block will attempt to update the patient summary if the new reading is within 15 minutes of the last summary. If any error occurs during this process, it will be caught and logged, but it will not affect the successful creation of the reading or the response to the client.
            try:
                patient_id = serializer.validated_data['patient_id']
                patient_summary=PatientSummary.objects.filter(patient_id=patient_id).order_by('-created_at').first()
                if patient_summary and patient_summary.created_at >= timezone.now() - timedelta(minutes=15):
                    recorded_at = serializer.validated_data['reading'].get('recorded_at')
                    if recorded_at<=patient_summary.created_at:
                        new_reading = serializer.validated_data['reading']
                        updated_readings = [new_reading] + patient_summary.readings[:-1]
                        patient=Patient.objects.get(patient_id=patient_id)
                        in_range=sum(1 for r in updated_readings if patient.low_threshold_glucose_mgdl <= r.get("glucose_mgdl", 0) <= patient.high_threshold_glucose_mgdl)
                        new_time_in_range_pct = (in_range / len(updated_readings)) * 100 if updated_readings else 0
                        patient_summary.readings = updated_readings
                        patient_summary.time_in_range_pct = new_time_in_range_pct
                        patient_summary.save()
            except Exception as e:
                print(f"Created successfully. But had error updating patient summary: {e}")

            
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

            time_in_range_pct = calculate_time_in_range_pct(readings, patient.low_threshold_glucose_mgdl, patient.high_threshold_glucose_mgdl)
            PatientSummary.objects.create(
                patient_id=patient_id,
                time_in_range_pct=time_in_range_pct,
                readings=[r.reading for r in readings],
                created_at=timezone.now()
                )
            
            return Response({
                "patient_id": patient_id,
                "time_in_range_pct": time_in_range_pct,
                "readings": [{
                    "device_id": reading.device_id,
                    "reading": reading.reading,
                    "evaluation": evaluate_glucose_reading(reading)
                } for reading in readings]
            }, status=status.HTTP_200_OK)
        
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        except Reading.DoesNotExist:
            return Response({"detail": "No readings found for this patient"}, status=status.HTTP_404_NOT_FOUND)