from django.core.exceptions import ValidationError

def validate_image(file):
    limit_mb = 5
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'Image too large — max {limit_mb} MB')
    if hasattr(file, 'content_type') and not file.content_type.startswith('image/'):
        raise ValidationError('Uploaded file is not an image')
