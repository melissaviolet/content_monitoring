from ..models import ContentItem
from django.utils.dateparse import parse_datetime

def load_mock_data():
    mock_data = [
        {
            "title": "Learn Django Fast",
            "body": "Django is a powerful Python framework",
            "source": "Blog A",
            "last_updated": "2026-03-20T10:00:00Z"
        },
        {
            "title": "Cooking Tips",
            "body": "Best recipes for beginners",
            "source": "Blog B",
            "last_updated": "2026-03-20T10:00:00Z"
        }
    ]

    for item in mock_data:
        ContentItem.objects.create(
            title=item["title"],
            body=item["body"],
            source=item["source"],
            last_updated=parse_datetime(item["last_updated"])
        )