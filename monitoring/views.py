from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword
from .serializers import KeywordSerilaizer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.content_loader import load_mock_data


class KeywordViewset(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerilaizer

@api_view(['POST'])
def import_content_view(request):
    load_mock_data()
    return Response({"message": "Content imported successfully."})