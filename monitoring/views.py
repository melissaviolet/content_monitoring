from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword, Flag, ContentItem
from .serializers import KeywordSerializer, FlagSerializer, ContentItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.content_loader import load_mock_data
from .services.scanner import run_scan
from .services.rag_chat import ask_rag_chatbot, get_context, _get_chain as build_chain
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

# Analyse page view
def analyse_page_view(request):
    return render(request, 'monitoring/analyse.html')

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


def _build_analysis_result(text: str):
    text = (text or '').strip()
    if not text:
        return {
            "summary": "",
            "relevance": "low",
            "reason": "No article text was provided.",
            "matched_keywords": [],
        }

    words = text.split()
    summary = text if len(words) <= 120 else ' '.join(words[:120]) + '...'

    matched_keywords = []
    seen = set()
    for keyword in Keyword.objects.all():
        name = keyword.name.strip()
        if not name:
            continue
        if name.lower() in text.lower() and name.lower() not in seen:
            matched_keywords.append(name)
            seen.add(name.lower())

    if matched_keywords:
        reason = (
            "Matched tracked keywords: "
            + ", ".join(matched_keywords)
            + "."
        )
        relevance = 'high' if len(matched_keywords) >= 2 else 'medium'
    else:
        reason = "No tracked keywords were directly detected in the article text."
        relevance = 'low'

    return {
        "summary": summary,
        "relevance": relevance,
        "reason": reason,
        "matched_keywords": matched_keywords,
    }


@api_view(['POST'])
def analyse_api_view(request):
    data = request.data or {}
    text = (data.get('text') or '').strip()

    if not text:
        return Response(
            {"error": "Please paste an article first."},
            status=400,
        )

    return Response(_build_analysis_result(text))


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

    # keep the public flow compatible with the tests while still using the
    # actual RAG implementation underneath
    context = get_context(question)
    chain = build_chain()
    result = chain.invoke({"context": context, "question": question})
    answer = result.content if hasattr(result, 'content') else str(result)

    recent_sources = list(
        ContentItem.objects.all().order_by('-last_updated').values('id', 'title')[:5]
    )

    return Response({
        "answer": answer,
        "sources": recent_sources
    })