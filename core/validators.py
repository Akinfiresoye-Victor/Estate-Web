import puremagic  # <--- Change 1: Updated import
from django.core.exceptions import ValidationError
import traceback

def validate_file(file):
    limit_mb = 10
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'File too large — maximum allowed size is {limit_mb} MB')

    file_content = file.read(2048)
    
    # Change 2: puremagic.from_string is the equivalent of magic.from_buffer
    try:
        file_type = puremagic.from_string(file_content, mime=True)
    except puremagic.PureError:
        file_type = "unknown/unknown"
        
    file.seek(0)

    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/jpeg',
        'image/png',
        'image/jpg',
        'image/webp',
    ]
    
    if file_type not in allowed_types:
        raise ValidationError(f'Unsupported file content ({file_type}). Please upload PDF, Word, or Image files.')

def validate_image(file):
    limit_mb = 5
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'Image too large — max {limit_mb} MB')

    file_content = file.read(2048)
    
    # Change 2: Same update here
    try:
        file_type = puremagic.from_string(file_content, mime=True)
    except puremagic.PureError:
        file_type = "unknown/unknown"
        
    file.seek(0)

    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
    
    if file_type not in allowed_types:
        raise ValidationError(f'Security Alert: File content is {file_type}, but only JPEG, PNG, and WebP are allowed.')