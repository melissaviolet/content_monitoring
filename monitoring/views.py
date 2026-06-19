from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword, Flag, ContentItem
from .serializers import KeywordSerializer, FlagSerializer, ContentItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.content_loader import load_mock_data
from .services.scanner import run_scan
from .services.rag_chat import ask_rag_chatbot
from django.utils import timezone


# Dashboard page view
def dashboard_view(request):
    return render(request, 'monitoring/dashboard.html')

# Flags page view
def flags_view(request):
    return render(request, 'monitoring/flags.html')

# Keywords page view
def keywords_view(request):
    return render(request, 'monitoring/keywords.html')

# Content page view
def content_view(request):
    return render(request, 'monitoring/content.html')

# Keyword viewset
class KeywordViewset(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer

# For import content mockup data 
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


# ── AI Chatbot endpoint ──
# Called by the floating widget on every page (chat-widget.js)
# Expects: { "question": "..." }
# Returns: { "answer": "...", "sources": [...] }
@api_view(['POST'])
def chatbot_query(request):
    data = request.data or {}
    question = (data.get('question') or '').strip()

    if not question:
        return Response({"answer": "Please ask a question first."}, status=400)

    # ask_rag_chatbot() does everything internally:
    # embeds the question, searches ChromaDB for relevant articles,
    # builds the prompt, sends it to Ollama, returns the answer text
    answer = ask_rag_chatbot(question)

    # Also return a few recent articles as "sources" so the
    # frontend could optionally show what the answer is based on
    recent_sources = list(
        ContentItem.objects.all().order_by('-last_updated').values('id', 'title')[:5]
    )

    return Response({
        "answer": answer,
        "sources": recent_sources
    })