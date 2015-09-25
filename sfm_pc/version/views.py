import json

from django.http import HttpResponse
from django.utils.translation import get_language

from complex_fields.models import ComplexFieldContainer

def get_versions(request, object_type, object_id, field_name, field_id=None,
                 lang=get_language()):
    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name, field_id
    )
    if field.translated:
        versions = field.get_history_for_lang(lang)
    else:
        versions = field.get_history()

    return HttpResponse(json.dumps(versions))

def revert_field(request, object_type, object_id, field_name):
    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )

    data = json.loads(request.POST.dict()['revert'])
    field.revert_field(data['lang'], data['id'])

    return HttpResponse(status=200)
