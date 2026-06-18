from django.shortcuts import render
from rest_framework import viewsets
from .models import Keyword, Flag, ContentItem
from .serializers import KeywordSerializer, FlagSerializer, ContentItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.content_loader import load_mock_data
from .services.scanner import run_scan
from django.utils import timezone

try:
    from langchain_ollama import ChatOllama
except Exception:
    ChatOllama = None

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


def _fallback_answer(question, content_items, keywords, flags):
    q = question.lower()
    if 'pending' in q or 'flag' in q:
        pending = flags.filter(status='pending').count()
        return f"There are currently {pending} pending flags awaiting review."

    if 'relevant' in q:
        relevant = flags.filter(status='relevant').count()
        return f"There are {relevant} relevant flags marked as relevant."

    if 'keyword' in q:
        return f"You have {keywords.count()} active keywords configured."

    if 'article' in q or 'content' in q:
        return f"The database currently contains {content_items.count()} content items."

    # Simple relevance scoring based on text overlap
    scored = []
    for item in content_items:
        text = f"{item.title} {item.body}".lower()
        score = sum(1 for word in q.split() if word in text)
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top = [item for score, item in scored[:3] if score > 0]
    if top:
        titles = ", ".join(item.title for item in top)
        return f"The most relevant articles appear to be: {titles}"

    return "I can help you review content, keywords, and flags. Try asking about pending flags, relevant items, or the number of articles."


@api_view(['POST'])
def chatbot_query(request):
    data = request.data or {}
    question = (data.get('question') or '').strip()

    if not question:
        return Response({"answer": "Please ask a question first."}, status=400)

    content_items = ContentItem.objects.all().order_by('-last_updated')
    keywords = Keyword.objects.all()
    flags = Flag.objects.select_related('keyword', 'content_item')

    # Try a real LLM if it is available; otherwise use a deterministic fallback.
    if ChatOllama is not None:
        try:
            llm = ChatOllama(model='qwen3:4b')
            context = "\n\n".join(
                f"Title: {item.title}\nSource: {item.source}\nBody: {item.body}"
                for item in content_items[:8]
            )
            prompt = (
                "You are a helpful assistant for a content monitoring dashboard. "
                "Use only the context below to answer the user's question. "
                f"Context:\n{context}\n\nQuestion: {question}"
            )
            answer = llm.invoke(prompt)
            answer_text = answer.content if hasattr(answer, 'content') else str(answer)
            return Response({
                "answer": answer_text,
                "sources": list(content_items.values('id', 'title')[:5])
            })
        except Exception:
            pass

    return Response({
        "answer": _fallback_answer(question, content_items, keywords, flags),
        "sources": list(content_items.values('id', 'title')[:5])
    })