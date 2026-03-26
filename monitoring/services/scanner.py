#For matching the scores 
def calculate_score(keyword, content):
    kw = keyword.name.lower()
    title = content.title.lower()
    body = content.body.lower()

    if kw in title.split():
        return 100
    elif kw in title:
        return 70
    elif kw in body:
        count = body.count(kw)
        return min(40 + (count*5), 60)
    return 0

#For scanning
from ..models import Keyword, ContentItem, Flag
from django.utils import timezone

def run_scan():
    keywords = Keyword.objects.all()
    contents = ContentItem.objects.all()

    for content in contents:
        for keyword in keywords:
            score = calculate_score(keyword, content)

            if score == 0:
                continue

            flag, created = Flag.objects.get_or_create(
                keyword=keyword,
                content_item=content,
                defaults={
                    'score': score,
                    'status': 'pending'
                }
            )

            #suppression logic
            if not created:
                if flag.status == 'irrelevant':
                    # only re-activate if content changed
                    if content.last_updated > flag.reviewed_at:
                        flag.status = 'pending'
                        flag.score = score
                        flag.save()
                else:
                    # update score if needed
                    flag.score = score
                    flag.save()