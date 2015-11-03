import json

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.template.loader import render_to_string
from django.views.generic.base import TemplateView
from django.utils.translation import ugettext as _
from django.http import HttpResponse
from django.db.models import Max

from organization.models import Classification
from composition.models import Composition


class CompositionView(TemplateView):
    template_name = 'composition/search.html'

    def get_context_data(self, **kwargs):
        context = super(CompositionView, self).get_context_data(**kwargs)

        order_by = self.request.GET.get('orderby')
        if not order_by:
            order_by = 'compositionstartdate__value'

        direction = self.request.GET.get('direction')
        if not direction:
            direction = 'ASC'

        dirsym = ''
        if direction == 'DESC':
            dirsym = '-'

        composition_query = (Composition.objects
                        .annotate(Max(order_by))
                        .order_by(dirsym + order_by + "__max"))

        classification = self.request.GET.get('classification')
        if classification:
            org_query = composition_query.filter(compositionrole__id=classification)

        context['composition'] = composition_query
        context['classifications'] = Classification.objects.all()

        return context

def composition_search(request):
    terms = request.GET.dict()

    composition_query = Composition.objects.all()
    page = int(terms.get('page', 1))

    column_names = [_('Parent'), _('Child'), _('Classification'), _('Start date'),
                     _('End date')]
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
        'column_names': column_names,
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
