import json
import csv
from datetime import date

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.contrib.admin.util import NestedObjects
from django.views.generic.edit import DeleteView
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.db import DEFAULT_DB_ALIAS

from organization.models import Classification
from composition.models import Composition
from sfm_pc.utils import deleted_in_str


class CompositionDelete(DeleteView):
    model = Composition
    template_name = "delete_confirm.html"

    def get_context_data(self, **kwargs):
        context = super(CompositionDelete, self).get_context_data(**kwargs)
        collector = NestedObjects(using=DEFAULT_DB_ALIAS)
        collector.collect([context['object']])
        deleted_elements = collector.nested()
        context['deleted_elements'] = deleted_in_str(deleted_elements)
        return context


    def get_object(self, queryset=None):
        obj = super(CompositionDelete, self).get_object()

        return obj


class CompositionView(TemplateView):
    template_name = 'composition/search.html'

    def get_context_data(self, **kwargs):
        context = super(CompositionView, self).get_context_data(**kwargs)

        context['classifications'] = Classification.objects.all()
        context['year_range'] = range(1950, date.today().year + 1)
        context['day_range'] = range(1, 32)

        return context


def composition_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="compositions.csv"'

    terms = request.GET.dict()
    composition_query = Composition.search(terms)

    writer = csv.writer(response)
    for composition in composition_query:
        writer.writerow([
            composition.id,
            composition.parent.get_value(),
            composition.child.get_value(),
            composition.classification.get_value(),
            repr(composition.startdate.get_value()),
            repr(composition.enddate.get_value()),
        ])

    return response


def composition_search(request):
    terms = request.GET.dict()

    composition_query = Composition.search(terms)

    page = int(terms.get('page', 1))

    keys = ['parent', 'child', 'classification', 'startdate', 'enddate']

    paginator = Paginator(composition_query, 15)
    try:
        composition_page = paginator.page(page)
    except PageNotAnInteger:
        person_page = paginator.page(1)
        page = 1
    except EmptyPage:
        person_page = paginator.page(paginator.num_pages)
        page = paginator.num_pages

    compositions = [
        {
            "id": composition.id,
            "parent": str(composition.parent.get_value()),
            "child": str(composition.child.get_value()),
            "classification": str(composition.classification.get_value()),
            "startdate": str(composition.startdate.get_value()),
            "enddate": str(composition.enddate.get_value()),
        }
        for composition in composition_page
    ]

    html_paginator = render_to_string(
        'paginator.html',
        {'actual': page, 'min': page - 5, 'max': page + 5,
         'paginator': composition_page,
         'pages': range(1, paginator.num_pages + 1)}
    )

    return HttpResponse(json.dumps({
        'success': True,
        'keys': keys,
        'objects': compositions,
        'paginator': html_paginator,
        'result_number': len(composition_query)
    }))


class CompositionUpdate(TemplateView):
    template_name = 'composition/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            composition = Composition.objects.get(pk=kwargs.get('pk'))
        except Composition.DoesNotExist:
            msg = "This composition does not exist, it should be created " \
                  "before updating it."
            return HttpResponse(msg, status=400)

        (errors, data) = composition.validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        composition.update(data)
        return HttpResponse(
            json.dumps({"success": True}),
            content_type="application/json"
        )

    def get_context_data(self, **kwargs):
        context = super(CompositionUpdate, self).get_context_data(**kwargs)
        context['composition'] = Composition.objects.get(pk=context.get('pk'))

        return context


class CompositionCreate(TemplateView):
    template_name = 'composition/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['object'])
        (errors, data) = Composition().validate(data)
        if len(errors):
            return HttpResponse(
                json.dumps({"success": False, "errors": errors}),
                content_type="application/json"
            )

        composition = Composition.create(data)

        return HttpResponse(json.dumps({"success": True, "id": composition.id}),
                            content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(CompositionCreate, self).get_context_data(**kwargs)
        context['composition'] = Composition()

        return context
