from django import template

register = template.Library()

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

