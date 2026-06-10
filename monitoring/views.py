from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword, Flag
from .serializers import KeywordSerializer, FlagSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.content_loader import load_mock_data
from .services.scanner import run_scan
from django.utils import timezone

#Keyword viewset
class KeywordViewset(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

#For import content mockup data 
@api_view(['POST'])
def import_content_view(request):
    load_mock_data()
    return Response({"message": "Content imported successfully."})

#For review and suppression
class FlagViewSet(viewsets.ModelViewSet):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer

    def perform_update(self, serializer):
        instance = serializer.save()
        
        # if reviewer marks it
        if instance.status in ['relevant', 'irrelevant']:
            instance.reviewed_at = timezone.now()
            instance.save()

#for scan, API endpoint
@api_view(['POST'])
def scan_view(request):
    run_scan()
    return Response({"message": "Scan completed"})