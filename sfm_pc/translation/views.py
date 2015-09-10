import json

from django.core.exceptions import ValidationError
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseServerError
from django.db.models import Q

from languages_plus.models import Language

from complex_fields.models import ComplexFieldContainer

def translate(request, object_type, object_id, field_name):
    data = json.loads(request.POST.dict()['translation'])

    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )

    try:
        field.translate(data['value'], data['lang'])
    except ValidationError as error:
        return HttpResponseServerError(str(error))

    return HttpResponse(status=200)

def autocomplete_language(request):
    data = request.GET.dict()['term']

    langs = Language.objects.filter(
        Q(name_en__icontains=data) |
        Q(name_native__icontains=data) |
        Q(name_other__icontains=data) |
        Q(iso_639_1__icontains=data)
    )
    import ipdb; ipdb.set_trace()
    languages = [
        lang.name_native
        for lang in langs.all()
    ]

    return HttpResponse(json.dumps(languages))
