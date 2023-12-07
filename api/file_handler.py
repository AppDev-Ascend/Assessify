import os
from django.conf import settings


def handle_uploaded_file(file):
    with open(os.path.join(settings.MEDIA_ROOT, 'files', file.name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

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