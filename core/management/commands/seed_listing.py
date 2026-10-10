from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from companies.models import CompanyInformation
from core.models import PropertyManagementRent, PropertyManagementSale


USER_ID = 2
DEFAULT_IMAGE_DIR = Path(r'C:\Users\User\Pictures\wallpapers')
MAX_IMAGE_SIZE = 5 * 1024 * 1024

SALE_LISTINGS = [
    {
        'location': 'Lekki Phase 1, Lagos',
        'state': 'Lagos',
        'price': '185000000',
        'bedrooms': 4,
        'bathrooms': 5,
        'size': 320,
        'residential': 'Detached Duplex',
        'description': 'Contemporary four-bedroom detached duplex with spacious en-suite bedrooms, a fitted kitchen, ample parking, and 24-hour estate security.',
    },
    {
        'location': 'Ikeja GRA, Lagos',
        'state': 'Lagos',
        'price': '240000000',
        'bedrooms': 5,
        'bathrooms': 5,
        'size': 410,
        'residential': 'Detached',
        'description': 'Well-finished five-bedroom family home in a quiet, secure neighbourhood, with generous living areas and a private garden.',
    },
    {
        'location': 'Ajah, Lagos',
        'state': 'Lagos',
        'price': '98000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 280,
        'residential': 'Terraced Duplex',
        'description': 'Modern four-bedroom terrace with fitted wardrobes, a fitted kitchen, treated water, and easy access to the Lekki-Epe Expressway.',
    },
    {
        'location': 'Yaba, Lagos',
        'state': 'Lagos',
        'price': '125000000',
        'bedrooms': 3,
        'bathrooms': 3,
        'size': 210,
        'residential': 'Apartment',
        'description': 'Bright three-bedroom apartment in a serviced development with lift access, reliable security, and dedicated parking.',
    },
    {
        'location': 'Gwarinpa, Abuja',
        'state': 'FCT',
        'price': '155000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 350,
        'residential': 'Detached Duplex',
        'description': 'Four-bedroom detached duplex with a spacious compound, fitted kitchen, family lounge, and secure gated access.',
    },
    {
        'location': 'Wuse 2, Abuja',
        'state': 'FCT',
        'price': '320000000',
        'bedrooms': 4,
        'bathrooms': 5,
        'size': 390,
        'residential': 'Penthouse',
        'description': 'Premium four-bedroom penthouse with generous entertaining space, contemporary finishes, and secure on-site parking.',
    },
    {
        'location': 'Bodija, Ibadan',
        'state': 'Oyo',
        'price': '85000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 360,
        'residential': 'Bungalow',
        'description': 'Spacious four-bedroom bungalow on a quiet street, featuring a large compound, fitted kitchen, and room for additional parking.',
    },
    {
        'location': 'GRA, Benin City',
        'state': 'Edo',
        'price': '110000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 330,
        'residential': 'Detached House',
        'description': 'Newly finished four-bedroom detached home with en-suite rooms, a family lounge, and a paved, fenced compound.',
    },
    {
        'location': 'Independence Layout, Enugu',
        'state': 'Enugu',
        'price': '135000000',
        'bedrooms': 5,
        'bathrooms': 5,
        'size': 400,
        'residential': 'Detached Duplex',
        'description': 'Five-bedroom home in a well-connected neighbourhood, with spacious interiors, secure parking, and a landscaped yard.',
    },
    {
        'location': 'Idu Industrial District, Abuja',
        'state': 'FCT',
        'price': '275000000',
        'bedrooms': 0,
        'bathrooms': 2,
        'size': 900,
        'property_category': 'Commercial',
        'commercial': 'Warehouse',
        'description': 'Secure warehouse facility with a broad loading area, office space, and convenient access to major transport routes.',
    },
]

RENT_LISTINGS = [
    {
        'location': 'Victoria Island, Lagos',
        'state': 'Lagos',
        'price_range': '8500000',
        'bedrooms': 3,
        'bathrooms': 3,
        'size': 220,
        'residential': 'Apartment',
        'description': 'Furnished three-bedroom apartment with en-suite rooms, a fitted kitchen, and 24-hour power and security.',
    },
    {
        'location': 'Ikoyi, Lagos',
        'state': 'Lagos',
        'price_range': '18000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 350,
        'residential': 'Serviced Apartment',
        'description': 'Serviced four-bedroom apartment in a secure development with lift access, a pool, a gym, and dedicated parking.',
    },
    {
        'location': 'Surulere, Lagos',
        'state': 'Lagos',
        'price_range': '3200000',
        'bedrooms': 2,
        'bathrooms': 2,
        'size': 125,
        'residential': 'Apartment',
        'description': 'Neat two-bedroom apartment with a fitted kitchen, treated water, and convenient access to public transport.',
    },
    {
        'location': 'Chevron Drive, Lekki, Lagos',
        'state': 'Lagos',
        'price_range': '6500000',
        'bedrooms': 3,
        'bathrooms': 3,
        'size': 190,
        'residential': 'Terraced Duplex',
        'description': 'Three-bedroom terrace in a gated estate with en-suite rooms, a fitted kitchen, and round-the-clock security.',
    },
    {
        'location': 'Jabi, Abuja',
        'state': 'FCT',
        'price_range': '7000000',
        'bedrooms': 3,
        'bathrooms': 3,
        'size': 210,
        'residential': 'Apartment',
        'description': 'Well-maintained three-bedroom apartment with a balcony, fitted kitchen, reliable water supply, and secure parking.',
    },
    {
        'location': 'Maitama, Abuja',
        'state': 'FCT',
        'price_range': '16000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 340,
        'residential': 'Detached Duplex',
        'description': 'Four-bedroom detached home with a private garden, spacious living areas, fitted kitchen, and secure compound.',
    },
    {
        'location': 'New GRA, Port Harcourt',
        'state': 'Rivers',
        'price_range': '5500000',
        'bedrooms': 3,
        'bathrooms': 3,
        'size': 200,
        'residential': 'Apartment',
        'description': 'Three-bedroom apartment in a secure residential area with ample parking and a steady water supply.',
    },
    {
        'location': 'GRA, Ikeja, Lagos',
        'state': 'Lagos',
        'price_range': '12000000',
        'bedrooms': 4,
        'bathrooms': 4,
        'size': 300,
        'residential': 'Semi Detached Duplex',
        'description': 'Four-bedroom semi-detached duplex with en-suite rooms, a family lounge, fitted kitchen, and gated access.',
    },
    {
        'location': 'Bodija, Ibadan',
        'state': 'Oyo',
        'price_range': '2800000',
        'bedrooms': 2,
        'bathrooms': 2,
        'size': 140,
        'residential': 'Bungalow',
        'description': 'Comfortable two-bedroom bungalow with a private outdoor area, fitted kitchen, and secure parking.',
    },
    {
        'location': 'Central Business District, Abuja',
        'state': 'FCT',
        'price_range': '9500000',
        'bedrooms': 0,
        'bathrooms': 2,
        'size': 180,
        'property_category': 'Commercial',
        'commercial': 'Office Space',
        'description': 'Ready-to-occupy office suite with a reception area, two washrooms, secure building access, and parking.',
    },
]


class Command(BaseCommand):
    help = 'Create 10 sample sale listings and 10 sample lease listings for Estate Web.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-dir',
            type=Path,
            default=DEFAULT_IMAGE_DIR,
            help='Folder containing listing images (defaults to the provided wallpapers folder).',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        try:
            user = User.objects.get(pk=USER_ID)
        except User.DoesNotExist as exc:
            raise CommandError(f'User #{USER_ID} does not exist.') from exc

        companies = [
            company
            for company in CompanyInformation.objects.filter(user=user)
            if ''.join(company.company_name.split()).casefold() == 'estateweb'
        ]
        if len(companies) != 1:
            raise CommandError(
                f'Expected one Estate Web company for user #{USER_ID}; found {len(companies)}.'
            )
        company = companies[0]

        image_dir = options['image_dir']
        if not image_dir.is_dir():
            raise CommandError(f'Image folder does not exist: {image_dir}')
        images = sorted(
            (
                path for path in image_dir.iterdir()
                if path.is_file()
                and path.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
                and path.stat().st_size <= MAX_IMAGE_SIZE
            ),
            key=lambda path: path.name.casefold(),
        )
        if not images:
            raise CommandError(
                f'No supported images up to 5 MB were found in {image_dir}.'
            )

        created_sale = self._seed_model(
            PropertyManagementSale,
            SALE_LISTINGS,
            'property_description',
            user,
            company,
            images,
            rent=False,
        )
        created_rent = self._seed_model(
            PropertyManagementRent,
            RENT_LISTINGS,
            'description',
            user,
            company,
            images,
            rent=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_sale} sale and {created_rent} lease listings '
            f'for user #{USER_ID} ({company.company_name}).'
        ))

    def _seed_model(self, model, listings, description_field, user, company, images, rent):
        created = 0
        for index, listing in enumerate(listings):
            description = listing['description']
            lookup = {
                'user': user,
                'company_uuid': company.unique_company_id,
                description_field: description,
            }
            if model.objects.filter(**lookup).exists():
                continue

            defaults = {
                **listing,
                'phone_number': company.phone_number,
                'company_uuid': company.unique_company_id,
                'is_listed': True,
                'property_type': 'Rent' if rent else 'Sale',
            }
            defaults[description_field] = defaults.pop('description')
            if rent:
                defaults['rent_rate'] = 'Yearly'

            property_obj = model(user=user, **defaults)
            image_path = images[index % len(images)]
            with image_path.open('rb') as image_file:
                property_obj.base_image = File(image_file, name=image_path.name)
                property_obj.full_clean()
                property_obj.save()
            created += 1

        return created
