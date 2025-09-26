#Getting and loading all the images for our webpage


from django import template

#What is used to preload the images before putting them on the screen
register = template.Library()



#used to get or preload the images
@register.filter

#function to get all the images 
def get_images(prop):
    return [img for img in [prop.image1, prop.image2, prop.image3, prop.image4, prop.image5, prop.image6] if img]
