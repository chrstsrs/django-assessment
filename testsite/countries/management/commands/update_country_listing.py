import json
import urllib.error
import urllib.request
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from countries.models import Country, Region


class Command(BaseCommand):
    help = "Loads country data from a JSON file."

    def get_data(self):
        url = settings.COUNTRIES_SOURCE_URL
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                if resp.status != 200:
                    raise CommandError(f"HTTP {resp.status} on fetching {url}")
                charset = resp.headers.get_content_charset() or "utf-8"
                raw = resp.read().decode(charset, errors="replace")
                return json.loads(raw)
        except (urllib.error.HTTPError, urlib.error.URLError) as e:
            raise CommandError(f"Error fetching data: {e}") from e
        except json.JSONDecodeError as e:
            raise CommandError(f"Invalid JSON: {e}") from e

    def handle(self, *args, **options):
        data = self.get_data()
        for row in data:
            region, region_created = Region.objects.get_or_create(name=row["region"])
            if region_created:
                self.stdout.write(
                    self.style.SUCCESS("Region: {} - Created".format(region))
                )
            tlds = row.get("topLevelDomain") or []
            tlds_str = ",".join(tlds)

            country, country_created = Country.objects.update_or_create(
                name=row["name"],
                defaults={
                    "alpha2Code": row["alpha2Code"],
                    "alpha3Code": row["alpha3Code"],
                    "population": row["population"],
                    "region": region,
                    "topLevelDomain": tlds_str,
                    "capital": row["capital"],
                },
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "{} - {}".format(
                        country, "Created" if country_created else "Updated"
                    )
                )
            )
