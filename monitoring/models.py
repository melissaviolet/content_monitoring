from django.db import models

class Keyword(models.Model):
    name = models.CharField(max_length=255)

class ContentItem(models.Model):
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=100)
    body = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

class Flag(models.Models):
    status_choices = [
        ('pending','Pending'),
        ('relevant', 'Relevant'),
        ('irrelevant', 'Irrelevant')
    ]


    keyword = models.ForeignKey(Keyword,on_delete=models.CASCADE)
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    score = models.IntegerField()
    status = models.CharField(max_length=20,choices= status_choices, default='pending')
    #for supression logic
    reviewed_at = models.DateTimeField(null=True, blank=True)
