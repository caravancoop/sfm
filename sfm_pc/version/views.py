import json

from django.http import HttpResponse
from django.utils.translation import get_language

from complex_fields.models import ComplexFieldContainer

def get_versions(request, object_type, object_id, field_name,
                 lang=get_language()):
    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )
    versions = field.get_history_for_lang(lang)

    return HttpResponse(json.dumps(versions))

