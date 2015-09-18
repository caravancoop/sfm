import json

from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse

from .models import Organization


class OrganizationCreate(TemplateView):
    template_name = 'organization/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['organization'])
        organization = Organization.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(OrganizationCreate, self).get_context_data(**kwargs)
        context['organization'] = Organization()

        return context
