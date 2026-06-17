from ..models import ContentItem
from django.utils.dateparse import parse_datetime


# This list lives here, in ONE place.
# Both the "Import Content" button AND the seed_data command
# pull from this same list — no more duplication.
MOCK_ARTICLES = [
    {
        "title": "AI Models Are Getting Smarter Every Year",
        "body": "Artificial intelligence and machine learning models have seen rapid growth. Companies like OpenAI and Google are pushing the boundaries of what AI can do. The latest language models show remarkable reasoning abilities.",
        "source": "Tech Daily",
        "last_updated": "2026-03-20T10:00:00Z"
    },
    {
        "title": "Election Results Spark Nationwide Debate",
        "body": "The recent election has led to widespread discussion about voting systems and democracy. Several candidates have raised concerns about election integrity and the counting process.",
        "source": "News Central",
        "last_updated": "2026-03-21T08:00:00Z"
    },
    {
        "title": "Climate Change Report: Urgent Action Needed",
        "body": "A new climate report warns that global temperatures are rising faster than predicted. Scientists say climate change is already affecting weather patterns, food security, and coastal regions worldwide.",
        "source": "Science Weekly",
        "last_updated": "2026-03-22T09:00:00Z"
    },
    {
        "title": "New Vaccine Shows Promising Results",
        "body": "Researchers have developed a new vaccine that shows strong immune response in early trials. Health officials are optimistic but stress that more testing is needed before the vaccine can be approved.",
        "source": "Health Today",
        "last_updated": "2026-03-23T11:00:00Z"
    },
    {
        "title": "Django Framework Releases Major Update",
        "body": "The Django web framework has released version 5.0 with significant improvements to performance and security. Python developers are excited about the new async capabilities and improved ORM features. Django continues to be a top choice.",
        "source": "Blog A",
        "last_updated": "2026-03-24T14:00:00Z"
    },
    {
        "title": "Social Media and Mental Health: What the Research Says",
        "body": "Multiple studies now link heavy social media use to increased anxiety and depression, especially in teenagers. Researchers are calling for stricter regulation of algorithms that promote addictive behaviour on social media platforms.",
        "source": "Psychology Now",
        "last_updated": "2026-03-25T10:00:00Z"
    },
    {
        "title": "Cryptocurrency Market Sees Wild Swings",
        "body": "Bitcoin and other cryptocurrencies experienced extreme volatility this week. Analysts are divided on whether this represents a healthy correction or the beginning of a larger crypto market collapse.",
        "source": "Finance Watch",
        "last_updated": "2026-03-26T16:00:00Z"
    },
    {
        "title": "Python vs JavaScript: The Endless Debate",
        "body": "Developers continue to argue about which language is better for beginners. Python dominates data science and machine learning while JavaScript remains the king of web development. Both Python and JS have seen massive growth.",
        "source": "Blog A",
        "last_updated": "2026-03-27T12:00:00Z"
    },
]


def load_mock_data():
    """
    Called when the user clicks 'Import Content' on the website.
    Uses get_or_create so clicking the button multiple times
    doesn't create duplicate articles.
    """
    for item in MOCK_ARTICLES:
        ContentItem.objects.get_or_create(
            title=item["title"],
            defaults={
                "body": item["body"],
                "source": item["source"],
                "last_updated": parse_datetime(item["last_updated"]),
            }
        )