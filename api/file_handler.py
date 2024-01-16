from django.http import HttpResponse
import mimetypes
import os
from django.conf import settings


def handle_uploaded_file(username, assessment_name, file, file_name):
    with open(os.path.join(settings.MEDIA_ROOT, rf'{username}/lessons/{assessment_name}', file_name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def download_file(request, file_path):
    # Build the file path
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)

    # Open the file in binary mode
    with open(file_path, 'rb') as file:
        # Get the file's content type using mimetypes
        content_type, _ = mimetypes.guess_type(file_path)
        
        # Create an HttpResponse with the file content
        response = HttpResponse(file.read(), content_type=content_type)
        
        # Set the Content-Disposition header to force download
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'

    return response

def handle_non_utf8(text):
    try:
        # Try to encode the text assuming it is UTF-8
        encoded_text = text.encode('utf-8')
        return text
    except UnicodeEncodeError:
        # Handle non-UTF-8 characters
        cleaned_text = clean_non_utf8_characters(text)
        return cleaned_text

def clean_non_utf8_characters(text):
    # Replace or remove non-UTF-8 characters
    cleaned_text = ''.join(char if char.isprintable() or char.isspace() else '?' for char in text)
    return cleaned_text