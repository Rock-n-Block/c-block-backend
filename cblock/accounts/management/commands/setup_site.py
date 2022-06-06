from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site

from cblock.settings import SITE_ID

class Command(BaseCommand):
    help = 'Setup Site name for django settings'

    def add_arguments(self, parser):
        parser.add_argument('domain', type=str, help='full domain name of site')
        parser.add_argument('site_name', type=str, help='Name of site')

    def handle(self, *args, **options):
        site = Site.objects.get(id=SITE_ID)
        site.domain = options['domain']
        site.name = options['site_name']
        site.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully changed site to {site.name} {site.domain}'))