from rest_framework import serializers
from .models import Keyword

class KeywordSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'