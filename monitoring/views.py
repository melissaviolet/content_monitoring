from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword
from .serializers import KeywordSerilaizer

class KeywordViewset(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerilaizer