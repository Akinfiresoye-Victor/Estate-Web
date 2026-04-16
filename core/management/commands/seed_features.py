from django.core.management.base import BaseCommand
from core.models import PropertyFeatures

class Command(BaseCommand):
    help = 'Seeds the property features list'

    def handle(self, *args, **kwargs):
        features = [
            # General
            'Swimming Pool', 'Gym', 'Security Post', 'CCTV Cameras',
            # Utilities
            'Electricity 24/7', 'Borehole', 'Water Treatment Plant', 'Solar Power',
            # Interior
            'En-suite', 'Fully Fitted Kitchen', 'Pop Ceiling', 'Walk-in Closet',
            # External
            'Ample Parking Space', 'Children Play Area', 'Green Area', 'Paved Compound',
            # Commercial/Industrial
            'Elevator', 'Fire Alarm', 'Loading Bay',
            # Documentation (Optional, if not handled elsewhere)
            'C of O', 'Governor’s Consent', 'Excision', 'Registered Survey'
            # Security & Technology
            'Biometric Access', 'Electric Fence', 'Video Doorbell', 'Smart Lighting',
            # Interior Luxury
            'Island Kitchen', 'Heat Extractor', 'Inbuilt Speakers', 'Home Cinema',
            # Infrastructure
            'Industrial Borehole', 'Solar Street Lights', 'Central Gas System',
            # Commercial
            'Fiber Optic Internet', 'Soundproof Boardroom', 'Fire Sprinklers',
            # Land
            'Table Land', 'Perimeter Fencing', 'Topography: Flat', 'Irrigation System'
        ]

        for feature_name in features:
            obj, created = PropertyFeatures.objects.get_or_create(name=feature_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created: {feature_name}'))
            else:
                self.stdout.write(f'Already exists: {feature_name}')