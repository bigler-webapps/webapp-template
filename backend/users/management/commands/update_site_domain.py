from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
from urllib.parse import urlparse
from django.conf import settings


class Command(BaseCommand):
    help = 'Updates the default Site object (ID=1) with the current domain from settings.'

    def handle(self, *args, **options):
        # Wir nehmen die PUBLIC_ORIGIN aus den settings (wird via .env gesetzt)
        # z.B. "https://template.bigler-consult.ch"
        public_origin = getattr(settings, 'PUBLIC_ORIGIN', None)

        if not public_origin:
            self.stdout.write(self.style.WARNING('PUBLIC_ORIGIN not set in settings. Skipping site update.'))
            return

        # Protokoll entfernen, falls vorhanden (https://domain.ch -> domain.ch)
        parsed = urlparse(public_origin)
        domain = parsed.netloc if parsed.netloc else parsed.path 
        
        # Display Name etwas hübscher machen (Projektname oder Domain)
        # Wir nehmen hier einfach den Projektnamen oder Fallback auf Domain
        project_name = getattr(settings, "PROJECT_NAME", domain)


        site_id = getattr(settings, "SITE_ID", 1)
        site, _ = Site.objects.get_or_create(pk=site_id)
        
        if site.domain == domain and site.name == project_name:
            self.stdout.write(self.style.SUCCESS(f'Site is already set to {domain}. No changes needed.'))
            return

        site.domain = domain
        site.name = project_name
        site.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated Site (ID=1) to: {domain}'))