import magic
from django.core.exceptions import ValidationError
import traceback

def validate_file(file):
    # 1. Size Check (10MB is usually plenty for PDFs/Docs)
    limit_mb = 10
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'File too large — maximum allowed size is {limit_mb} MB')

    # 2. Deep Content Inspection
    file_content = file.read(2048)
    file_type = magic.from_buffer(file_content, mime=True)
    file.seek(0)  # Always reset the pointer!

    # 3. Expanded Allowed Types
    allowed_types = [
        # Documents
        'application/pdf',
        'application/msword',                                               # .doc
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', # .docx
        
        # Images (in case they upload a scanned document as an image)
        'image/jpeg',
        'image/png',
        'image/jpg',
        'image/webp',
    ]
    
    if file_type not in allowed_types:
        # Note: If a .docx fails, file_type might show as 'application/zip' 
        # because Office files are technically zipped XML.
        raise ValidationError(f'Unsupported file content ({file_type}). Please upload PDF, Word, or Image files.')


def validate_image(file):
    # 1. Size Check
    limit_mb = 5
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'Image too large — max {limit_mb} MB')

    # 2. Deep Content Inspection (Magic Bytes)
    # We read the first 2048 bytes to determine the true file type
    file_content = file.read(2048)
    file_type = magic.from_buffer(file_content, mime=True)
    file.seek(0)  # CRITICAL: Reset file pointer so Django can still save the file

    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg']
    
    if file_type not in allowed_types:
        raise ValidationError(f'Security Alert: File content is {file_type}, but only JPEG, PNG, and WebP are allowed.')
