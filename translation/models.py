from django.utils.translation import get_language
from languages_plus.models import Language


def get_language_from_iso(iso):
    try:
        lang = Language.objects.get(iso_639_1=iso)
    except Language.DoesNotExist:
        return "Unknown"

    if iso == get_language():
        return lang.name_en
    else:
        return lang.name_en + ", " + lang.name_native
