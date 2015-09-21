import json

from django.views.generic.edit import UpdateView
from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse

from organization.models import Organization
from .models import Membership


class MembershipCreate(TemplateView):
    template_name = 'membership/edit.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        data = json.loads(request.POST.dict()['membership'])
        membership = Membership.create(data)

        return HttpResponse(json.dumps({"success": True}), content_type="application/json")

    def get_context_data(self, **kwargs):
        context = super(MembershipCreate, self).get_context_data(**kwargs)
        context['membership'] = Membership()

        return context
