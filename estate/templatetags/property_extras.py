from django import template

register = template.Library()

@register.filter
def role_base(user):
    """Return the base template path for a user role."""
    if not user or not hasattr(user, 'role') or not user.role:
        return 'estate/base.html'

    role = user.role.lower().strip()
    if role == 'customer':
        return 'estate/base.html'
    if role in ['agent', 'company']:
        return f'{role}/base.html'

    return 'estate/base.html'

@register.filter
def get_images(prop):
    # Start with the base image, if it exists
    image_list = []
    if hasattr(prop, 'base_image') and prop.base_image:
        image_list.append(prop.base_image)
    
    # Add related images from the related model (through the 'images' related_name)
    if hasattr(prop, 'images'):
        for related_image in prop.images.all():
            if hasattr(related_image, 'more_images') and related_image.more_images:
                image_list.append(related_image.more_images)
    
    return image_list

