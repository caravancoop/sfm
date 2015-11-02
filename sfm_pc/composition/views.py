import json

from django.views.generic.base import TemplateView
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
            org_query = composition_query.filter(membershiprole__id=classification)

        context['composition'] = composition_query
        context['classifications'] = Classification.objects.all()

        return context


class CompositionUpdate(TemplateView):
    template_name = 'composition/edit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.POST.dict()['object'])
        try:
            composition = Composition.objects.get(pk=kwargs.get('pk'))
        except Composition.DoesNotExist:
            msg = "This membership does not exist, it should be created " \
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
