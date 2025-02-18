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


import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, FileResponse
from django.contrib import messages
from .models import UploadedFile
from django.core.files.base import ContentFile
from django.contrib.auth.decorators import login_required, user_passes_test

# Temporary folder for file uploads in Vercel
TEMP_UPLOAD_DIR = "/tmp"

def developer(request):
    message = ""
    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, uploaded_file.name)

        # Save file to /tmp/ before processing
        with open(temp_file_path, "wb+") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Save file reference in DB (without actual file storage)
        new_file = UploadedFile(file=uploaded_file)  # DB entry for reference
        new_file.save()
        
        message = "File uploaded successfully!"
    else:
        message = "No file selected."

    return render(request, "news/developer.html", {"message": message})


@login_required
def view_uploaded_files(request):
    if not request.user.is_superuser:
        messages.warning(request, "You do not have permission to view uploaded files.")
        return redirect('home')

    files = UploadedFile.objects.all()
    return render(request, "news/view_files.html", {"files": files})


@login_required
def view_file_content(request, file_id):
    file = get_object_or_404(UploadedFile, id=file_id)
    
    temp_file_path = os.path.join(TEMP_UPLOAD_DIR, os.path.basename(file.file.name))

    # Check if file exists in /tmp/ (if not, re-fetch from DB)
    if not os.path.exists(temp_file_path):
        with open(temp_file_path, "wb+") as temp_file:
            temp_file.write(file.file.read())

    # Return file content based on type
    if file.file.name.endswith(".txt"):
        with open(temp_file_path, "r") as f:
            content = f.read()
        return HttpResponse(content, content_type="text/plain")
    
    elif file.file.name.endswith((".jpg", ".png")):
        return FileResponse(open(temp_file_path, "rb"), content_type="image/jpeg")
    
    elif file.file.name.endswith(".pdf"):
        return FileResponse(open(temp_file_path, "rb"), content_type="application/pdf")
    
    return HttpResponse("Unsupported file type", status=415)
