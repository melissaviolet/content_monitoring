from rest_framework import serializers
from .models import Keyword, ContentItem

#Keyword serializer
class KeywordSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = '__all__'

#ContentItem serializer
class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = '__all__'