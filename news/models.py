from django.db import models

class NewsArticle(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField()
    image_url = models.URLField(default="https://via.placeholder.com/600x400")
    published_at = models.DateTimeField(auto_now_add=True)  # Stores timestamp automatically

    class Meta:
        ordering = ["-published_at"]  # Orders articles with newest at the top

    def __str__(self):
        return self.title
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

