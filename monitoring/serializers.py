from rest_framework import serializers
from .models import Keyword, ContentItem, Flag

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

#Flag serializer
class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = '__all__'