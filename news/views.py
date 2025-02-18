from django.shortcuts import render
from .models import NewsArticle
from django.shortcuts import render, redirect
from django.http import HttpResponse
# news/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import user_passes_test
from .models import UploadedFile
from django.contrib.auth.views import LoginView
def home(request):
    news = NewsArticle.objects.all().order_by('-published_at')[:50]
    return render(request, "news/home.html", {"news": news})


def developer(request):
    message = ""
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if uploaded_file:
            # Save the file in the database (and file system via FileField)
            new_file = UploadedFile(file=uploaded_file)
            new_file.save()
            message = "File uploaded successfully!"
        else:
            message = "No file selected."
    return render(request, "news/developer.html", {"message": message})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from .models import UploadedFile
import os

def view_uploaded_files(request):
    if not request.user.is_superuser:
        messages.warning(request, "You do not have permission to view the uploaded files.")
        return redirect('home')
    
    files = UploadedFile.objects.all()
    return render(request, 'news/view_files.html', {'files': files})

def view_file_content(request, file_id):
    file = UploadedFile.objects.get(id=file_id)
    file_path = file.file.path

    # Check file type and render content accordingly
    if file.file.name.endswith('.txt'):
        with open(file_path, 'r') as f:
            content = f.read()
        return HttpResponse(content, content_type="text/plain")
    elif file.file.name.endswith('.jpg') or file.file.name.endswith('.png'):
        return FileResponse(open(file_path, 'rb'), content_type="image/jpeg")
    elif file.file.name.endswith('.pdf'):
        return FileResponse(open(file_path, 'rb'), content_type="application/pdf")
    else:
        return HttpResponse("File type not supported", status=415)





