from rest_framework import serializers
from .models import Keyword, ContentItem, Flag

#Keyword serializer
class KeywordSerializer(serializers.ModelSerializer):
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
    keyword_name = serializers.CharField(source='keyword.name', read_only=True)
    content_item_title = serializers.CharField(source='content_item.title', read_only=True)
    content_item_source = serializers.CharField(source='content_item.source', read_only=True)

    class Meta:
        model = Flag
        fields = [
            'id',
            'keyword',
            'keyword_name',
            'content_item',
            'content_item_title',
            'content_item_source',
            'score',
            'status',
            'reviewed_at',
        ]