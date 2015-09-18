import json

from django.http import HttpResponse
from django.utils.translation import get_language

from complex_fields.models import ComplexFieldContainer
from .models import Source

def get_sources(request, object_type, object_id, field_name):
    field = ComplexFieldContainer.field_from_str_and_id(
        object_type, object_id, field_name
    )
    sources = field.get_sources()
    sources_json = [
        {"source": source.source, "confidence": source.confidence}
        for source in sources
    ]

    return HttpResponse(json.dumps(sources_json))

def get_confidences(request):
    lang = request.GET.get('lang', get_language())
    return HttpResponse(json.dumps({
        "confidences": Source.get_confidences(lang)
    }))

