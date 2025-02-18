from django.contrib import admin
from .models import NewsArticle

# Register the NewsArticle model to make it available in the admin panel
admin.site.register(NewsArticle)

from .models import UploadedFile
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')  # Adjusting to the actual fields in the model
    search_fields = ('file',)

admin.site.register(UploadedFile, UploadedFileAdmin)


