from django.core.exceptions import ValidationError

def validate_image(file):
    limit_mb = 5
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'Image too large — max {limit_mb} MB')
    if hasattr(file, 'content_type') and not file.content_type.startswith('image/'):
        raise ValidationError('Uploaded file is not an image')


def validate_file(file):
    limit_mb = 10
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'File too large — maximum allowed size is {limit_mb} MB')

    allowed_types = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/jpg',
    ]
    if hasattr(file, 'content_type') and file.content_type not in allowed_types:
        raise ValidationError('Unsupported file type. Only PDF, JPG, and PNG files are allowed.')

