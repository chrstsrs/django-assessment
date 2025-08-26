from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Region


def stats(request):
    regions = (
        Region.objects
        .annotate(
            number_countries=Count("countries"),
            total_population=Sum("countries__population")
        )
        .values("name", "number_countries", "total_population")
        .order_by("name")
    )
    response = {
        "regions": list(regions)
    }

    return JsonResponse(response)
