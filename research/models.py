from django.db import models
from django.utils import timezone

# Create your models here.
class Document(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=50)
    date_filed = models.DateTimeField(default=timezone.now) 
    content = models.TextField()
    source_url = models.URLField(blank=True, null=True)
    chunks_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f'{self.company} - {self.title}'

class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content= models.TextField()
    embedding_generated = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.document.title} - Chunk {self.chunk_index}'