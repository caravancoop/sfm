import json

from django.core.exceptions import ValidationError
from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseServerError

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
