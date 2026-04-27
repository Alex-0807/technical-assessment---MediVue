from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework import status
from api.models import Reading, ReadingDeDupKey
from api.serializers import ReadingSerializer

# Create your views here.

class ReadingView(APIView):
    def post(self, request):
        serializer = ReadingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # Save the valid data to the database
        dedupKey = f"{serializer.validated_data['device_id']}_{serializer.validated_data['patient_id']}"
        if not ReadingDeDupKey.objects.filter(ReadingDeDupKey=dedupKey).exists():
            Reading.objects.create(**serializer.validated_data)
            ReadingDeDupKey.objects.create(ReadingDeDupKey=dedupKey)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Duplicate reading"}, status=status.HTTP_409_CONFLICT)
    def get(self, request):
        readings = Reading.objects.all()
        return Response([{
            "device_id": reading.device_id,
            "patient_id": reading.patient_id,
            "reading": reading.reading
        } for reading in readings], status=status.HTTP_200_OK)